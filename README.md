# FluxCam: Webcam Control Application

FluxCam is a real-time webcam control application that offers a live camera preview with `v4l2` controls and a variety of `OpenCV` effects. It provides a user-friendly interface to manage and enhance your webcam feed.

## Features

- **Real-time Camera Preview**: View your webcam feed with minimal latency.
- **v4l2 Controls**: Adjust camera settings like brightness, contrast, saturation, and more.
- **OpenCV Effects**: Apply a range of effects to your video feed, including:
    - Blur
    - Edge Detection
    - Cartoon
    - Sepia
    - Negative
    - Grayscale
    - Emboss
    - Sharpen
- **Video Transformations**:
    - Mirror (horizontal flip)
    - Flip (vertical flip)
    - Rotate (90, 180, 270 degrees)
- **Multi-camera Support**: Automatically detects and allows switching between multiple connected cameras.

## Requirements

- Python 3.x
- PyQt6
- OpenCV
- NumPy
- `v4l2-ctl` (usually part of the `v4l-utils` package)

## Installation & Usage

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/arnavpadwal/FluxCam.git
    cd FluxCam
    ```

2.  **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: You may need to create a `requirements.txt` file with the necessary dependencies: `PyQt6`, `opencv-python`, `numpy`)*

3.  **Ensure `v4l-utils` is installed:**
    - On Debian/Ubuntu:
      ```bash
      sudo apt-get update
      sudo apt-get install v4l-utils
      ```
    - On Fedora:
      ```bash
      sudo dnf install v4l-utils
      ```

4.  **Run the application:**
    ```bash
    python Flux_Cam.py
    ```

## Controls

- **Camera Source**: A dropdown menu to select the active webcam.
- **Video Effects**: A dropdown menu to apply different visual effects.
- **Video Transform**: Buttons to mirror, flip, and rotate the video feed.
- **Camera Controls**: A scrollable list of sliders to adjust `v4l2` camera settings. Each control has a reset button to revert to its default value.

## Future Plans

- [ ] **More Effects**: Add a wider variety of real-time video effects.
- [ ] **Video Recording**: Implement functionality to record the webcam feed.
- [ ] **Cross-platform Support**: Improve compatibility with Windows and macOS.
- [ ] **UI Enhancements**: Refine the user interface for a more modern look and feel.

## Contributing

Contributions are welcome! If you have any ideas, suggestions, or bug reports, please open an issue or submit a pull request.

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/your-feature`).
3.  Commit your changes (`git commit -m 'Add some feature'`).
4.  Push to the branch (`git push origin feature/your-feature`).
5.  Open a pull request.

## License

This project is licensed under the GNU General Public License v3.0. See the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues or have questions, please [open an issue](https://github.com/arnavpadwal/FluxCam/issues) on GitHub.
