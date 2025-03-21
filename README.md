# Voice to Text Tool

This program uses the VOSK offline speech recognition engine to convert speech from a microphone into text. It builds a simple GUI with DearPyGui.

## IMPORTANT NOTE

- This version uses a sample rate of 44100 Hz.
- Ensure that your microphone supports 44100 Hz.
- Also, ensure that the VOSK model is placed in a folder named `vosk_model` (for example, using `vosk-model-small-cn-0.22`).

## Project Structure
```
voice_to_text/ 
├── main.py 
├── README.md 
└── vosk_model/ <-- VOSK model folder
```

## Dependencies

To install the required dependencies, run:

```bash
pip install vosk sounddevice dearpygui
```

## Usage

1. Ensure that the VOSK model is placed in a folder named `vosk_model`.
2. Run the `main.py` script:

```bash
python main.py
```
3. The GUI will open. Select a microphone from the dropdown list and click "开始录制" to start recording. Click "停止录制" to stop recording and see the transcribed text.  


## Code Overview

### `main.py`

- **Imports**: Imports necessary libraries including `vosk`, `sounddevice`, and `dearpygui`.
- **Global Variables**: Defines the sample rate and a global variable to hold the recording thread instance.
- **RecordThread Class**: A thread class for recording and recognizing speech.
- **Microphone Device Dictionary**: Constructs a dictionary of available microphone devices.
- **Callbacks**: Defines callbacks for starting and stopping the recording.
- **GUI**: Builds the GUI using DearPyGui.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
