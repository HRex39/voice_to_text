"""
Voice to Text Tool
==================
This program uses the VOSK offline speech recognition engine to convert speech
from a microphone into text. It builds a simple GUI with DearPyGui.

IMPORTANT NOTE:
    This version uses a sample rate of 44100 Hz.
    Ensure that your microphone supports 44100 Hz.
    Also, ensure that the VOSK model is placed in a folder named "vosk_model"
    (for example, using vosk-model-small-cn-0.22).

Project structure:
    voice_to_text/
    ├── main.py
    └── vosk_model/   <-- VOSK model folder

Dependencies:
    pip install vosk sounddevice dearpygui
"""

import threading
import json
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import dearpygui.dearpygui as dpg

# Set the sample rate here.
SAMPLE_RATE = 44100

# Global variable to hold the recording thread instance.
record_thread = None

# Recording and recognition thread.
class RecordThread(threading.Thread):
    def __init__(self, device_index, sample_rate):
        super().__init__()
        self.device_index = device_index
        self.sample_rate = sample_rate  # Use the defined SAMPLE_RATE
        self.running = True
        self.result_text = ""
    
    def run(self):
        try:
            # Pass the model folder as a normal Python string.
            model = Model("vosk_model")
        except Exception as e:
            self.result_text = "Failed to load model: " + str(e)
            return

        recognizer = KaldiRecognizer(model, self.sample_rate)
        text = ""
        try:
            with sd.RawInputStream(
                samplerate=self.sample_rate,
                blocksize=8000,
                device=self.device_index,
                dtype='int16',
                channels=1
            ) as stream:
                while self.running:
                    data, _ = stream.read(8000)
                    if data:
                        # 将数据转换为字节字符串
                        data = bytes(data)
                        if recognizer.AcceptWaveform(data):
                            result = recognizer.Result()
                            jres = json.loads(result)
                            text += jres.get("text", "") + " "
        except Exception as e:
            text += "\nRecording error: " + str(e)
        
        # Append any remaining recognition output.
        final_result = recognizer.FinalResult()
        jres = json.loads(final_result)
        text += jres.get("text", "")
        self.result_text = text

    def stop(self):
        self.running = False

# 构造麦克风设备字典，进行简单过滤
input_devices = {}
devices = sd.query_devices()
for idx, dev in enumerate(devices):
    if dev.get("max_input_channels", 0) > 0:
        # 尝试过滤掉不可识别的字符
        name = dev["name"]
        try:
            name = name.encode("utf-8", "ignore").decode("utf-8")
        except Exception as e:
            pass
        input_devices[name] = idx

# Callback for "Start Recording".
def start_recording(sender, app_data, user_data):
    global record_thread, SAMPLE_RATE
    mic_name = dpg.get_value("mic_combo")
    print(f"Selected microphone: {mic_name}")  # Debugging line
    device_index = input_devices.get(mic_name)
    if device_index is None:
        dpg.set_value("output_text", "Please select a valid microphone device.")
        return

    # Retrieve the device's default sample rate.
    device_info = sd.query_devices(device_index, 'input')
    default_rate = device_info["default_samplerate"]
    print("Device default sample rate:", default_rate)
    
    # Check if the device sample rate matches SAMPLE_RATE (allowing a small tolerance).
    if abs(default_rate - SAMPLE_RATE) > 1:
        error_msg = f"Selected device does not support {SAMPLE_RATE} Hz audio (default: {default_rate} Hz)."
        dpg.set_value("output_text", error_msg)
        print(error_msg)
        SAMPLE_RATE = default_rate
        return

    # Create and start the recording thread.
    record_thread = RecordThread(device_index, SAMPLE_RATE)
    record_thread.start()
    dpg.configure_item("start_button", enabled=False)
    dpg.configure_item("stop_button", enabled=True)
    dpg.set_value("output_text", "Recording...")
    print("Recording started with device index:", device_index)  # Debugging line

# Callback for "Stop Recording".
def stop_recording(sender, app_data, user_data):
    global record_thread
    if record_thread is not None:
        record_thread.stop()
        record_thread.join()
        dpg.set_value("output_text", record_thread.result_text)
        record_thread = None
        print("Recording stopped.")
    dpg.configure_item("start_button", enabled=True)
    dpg.configure_item("stop_button", enabled=False)

# Build the GUI.
dpg.create_context()

# Load Chinese font
with dpg.font_registry():
    with dpg.font("fonts/NotoSansSC-Regular.ttf", 18) as font1:  # 增加中文编码范围，防止问号
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Chinese_Simplified_Common)
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Chinese_Full)
    dpg.bind_font(font1)

with dpg.window(tag="main_window", label="Voice to Text Tool", width=600, height=400):
    dpg.add_text("选择麦克风：")
    if input_devices:
        dpg.add_combo(
            list(input_devices.keys()),
            default_value=list(input_devices.keys())[0],
            tag="mic_combo"
        )
    else:
        dpg.add_text("No Detected Microphone")
    dpg.add_button(label="开始录制", callback=start_recording, tag="start_button")
    dpg.add_button(label="停止录制", callback=stop_recording, tag="stop_button", enabled=False)
    dpg.add_input_text(
        multiline=True,
        width=580,
        height=200,
        tag="output_text",
        default_value="",
        readonly=True
    )
    dpg.add_button(label="Exit", callback=lambda: dpg.stop_dearpygui())

dpg.create_viewport(title="VOICE_TO_TEXT", width=600, height=400)
dpg.setup_dearpygui()
dpg.set_primary_window("main_window", True)
dpg.show_viewport()


print("UI started. Entering event loop.")
dpg.start_dearpygui()
dpg.destroy_context()
