from multimedia_capture import capture
from parameter_capture  import capture_parameters

# Run the main function
if __name__ == "__main__":
    param_cap = capture_parameters.ParameterCapture()
    multi_cap = capture.Capture()
    
    multi_cap.run_capture()
    param_cap.run_capture()
