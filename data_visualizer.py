import argparse
from data_visualization import DataVisualizer
from utils import Log

def parse_arguments():
    parser = argparse.ArgumentParser(description="Data Visualizer Processor for creating animations from dataset files.")
    
    # Input/Output arguments
    parser.add_argument('--input_file', type=str, default='', help='CSV or TFRecord input file.')
    parser.add_argument('--input_dir', type=str, default='', help='Directory containing multiple dataset files.')
    parser.add_argument('--output_dir', type=str, required=True, help='Directory to save output animations.')
    
    # Format and file handling
    parser.add_argument('--data_input_format', type=str, choices=['csv', 'tfrecord'], default='csv', 
                        help='Input file format: "csv" or "tfrecord".')
    
    # Visualization options
    parser.add_argument('--csv_file', type=str, default='', 
                    help='CSV file in input to visualize.')
    parser.add_argument('--tfrecord_file', type=str, default='', 
                        help='TFRecord file in input to visualize.')
    
    parser.add_argument('--csv_file_index', type=int, default=-1, 
                        help='Index of CSV file in input directory to visualize.')
    parser.add_argument('--tf_file_index', type=int, default=-1, 
                        help='Index of TFRecord file in input directory to visualize.')
    parser.add_argument('--animation_name', type=str, default='', help='Custom name for the output animation file.')
    parser.add_argument('--output_format', type=str, default='.gif', choices=['.gif', '.mp4'], 
                        help='Format of the output animation, e.g., ".gif" or ".mp4".')
    parser.add_argument('--write',type=bool, default=True, help='Flag to save the animation to the output directory.')
    parser.add_argument('--verbose', type=str, default='INFO', choices=['DEBUG', 'ERROR', 'WARNING'])
    parser.add_argument('--encoding', type=str, default='ISO-8859-1', help='csv encoding.')
    
    
    return parser.parse_args()

def main():
    args = parse_arguments()

    try:

        # Initialize the DataVisualizerProcessor
        visualizer = DataVisualizer(
            input_file=args.input_file,
            input_dir=args.input_dir,
            output_dir=args.output_dir,
            data_input_format=args.data_input_format,
            encoding=args.encoding,
            verbose=args.verbose
        )

        # Create the animation based on specified parameters
        if args.data_input_format == 'csv':
            if args.csv_file_index >= 0:
                animation = visualizer.visualize_data(
                    csv_file_index=args.csv_file_index,
                    animation_name=args.animation_name,
                    write=args.write,
                    output_format=args.output_format
                )
            elif args.csv_file or '.csv' in args.input_file:
                animation = visualizer.visualize_data(
                    csv_file=args.csv_file,
                    animation_name=args.animation_name,
                    write=args.write,
                    output_format=args.output_format
                )
            else:
                print("CSV Invalid input!")

        elif args.data_input_format == 'tfrecord':
            if args.tf_file_index >= 0:
                animation = visualizer.visualize_data(
                    tf_file_index=args.tf_file_index,
                    animation_name=args.animation_name,
                    write=args.write,
                    output_format=args.output_format
                )
            elif args.tfrecord_file or '.tfrecord' in args.input_file:
                animation = visualizer.visualize_data(
                    tfrecord_file=args.tfrecord_file,
                    animation_name=args.animation_name,
                    write=args.write,
                    output_format=args.output_format
                )
            else:
                print("TFrecord_file Invalid input!")
    
    except ValueError as e:
        print(f"Error: {e}")
    except FileNotFoundError as e:
        print(f"Configuration loading failed: {e}")

if __name__ == "__main__":
    main()
