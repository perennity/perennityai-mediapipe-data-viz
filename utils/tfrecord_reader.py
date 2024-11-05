
import os
import sys
import glob
import numpy as np
import tensorflow as tf
from .csv_to_tfrecord_reader import CSVtoTFRecordConverter

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import configparser
config = configparser.ConfigParser()
config.read('configs/config.ini')

ALL_FEATURE_COLUMNS = config['all_features']['ALL_FEATURE_COLUMNS']

class TFCSVRecordReader:
    """
    A class for processing and managing TFRecord files for storing and reading landmark data 
    with optional conversion from CSV format.

    Attributes:
        num_features (int): The number of features per sample (e.g., landmarks).
        channels (int): The number of channels per feature (e.g., x, y, z coordinates).
        total_num_features (int): The total number of features after multiplying `num_features` by `channels`.
        landmark_output_shape (int): The output shape for landmarks; can be used to control reshape dimensions.
        input_file (str or list): Path to a single TFRecord file or list of file paths.
        file_pattern (str): The file pattern to match TFRecord or CSV files in the `input_path` directory.
        input_path (str): Directory path containing TFRecord or CSV files.
        feature_columns (list): List of feature column names.
        converter (CSVtoTFRecordConverter): Instance of a converter to convert CSV files to TFRecord format if needed.
        logger: Logger instance for logging purposes.

    Methods:
        __init__(self, input_file='', input_path='', landmark_output_shape=2, channels=3, num_features=543, feature_columns=[], data_input_format='csv', logger=None):
            Initializes the TFCSVRecordReader with specified parameters and file paths.
        
    Raises:
        ValueError: If the TFRecord path does not exist, no TFRecord files are found, or if an invalid file format is provided.
    """

    def __init__(self, input_file='', input_path='',
                 landmark_output_shape=2, channels=3, num_features=543,
                 feature_columns=[], data_input_format='csv', encoding='', logger=None):
        """
        Initializes the TFCSVRecordReader with necessary parameters for handling TFRecord data.

        Args:
            input_file (str, optional): Path to a single TFRecord file. Defaults to an empty string.
            input_path (str, optional): Path to a directory containing TFRecord or CSV files. Defaults to an empty string.
            landmark_output_shape (int, optional): The shape for outputting landmark data. Defaults to 2.
            channels (int, optional): Number of channels per feature, typically 3 for x, y, z. Defaults to 3.
            num_features (int, optional): Number of features per sample, typically the number of landmarks. Defaults to 543.
            feature_columns (list, optional): List of feature column names. Defaults to an empty list.
            data_input_format (str, optional): Specifies file format, either 'csv' or 'tfrecord'. Defaults to 'csv'.
            logger (optional): Logger instance for logging. Defaults to None.

        Raises:
            ValueError: If the specified TFRecord path does not exist or no TFRecord files are found.
            ValueError: If an invalid file format is provided in `data_input_format`.
        """
        
        self.num_features = num_features
        self.channels = channels
        self.total_num_features = num_features * channels
        self.landmark_output_shape = landmark_output_shape
        self.input_file = input_file
        self.file_pattern = None
        self.input_path = input_path
        self.feature_columns = feature_columns
        self.converter = None
        self.logger = logger

        # Handling single TFRecord file or converting CSV path to TFRecord paths
        if os.path.isfile(input_file):
            self.input_file = [input_file]
            self.input_path = os.path.dirname(input_file)

        # Set up TFRecord path and file pattern
        if self.input_path:
            if os.path.exists(self.input_path):
                if data_input_format != 'csv':
                    self.file_pattern = f'{self.input_path}/*.tfrecord'
                else:
                    self.file_pattern = f'{self.input_path}/*.csv'
                
                # Use glob to match files and verify
                self.input_file = glob.glob(self.file_pattern)
                if not self.input_file:
                    raise ValueError(f"No TFRecord files found in {self.input_path}")
            else:
                raise ValueError(f"TFRecord path {self.input_path} does not exist.")

        # Initialize CSV converter if using CSV format
        if 'csv' in data_input_format:
            self.converter = CSVtoTFRecordConverter(logger=self.logger, encoding=encoding)
            
        # Ensure valid file format is provided
        if not data_input_format or 'csv' not in data_input_format and 'tfrecord' not in data_input_format:
            raise ValueError('Provide valid file format')

        # Define feature descriptions for TFRecord parsing
        self.feature_description = {
            'frame': tf.io.FixedLenFeature([], tf.int64),
            'landmark': tf.io.VarLenFeature(tf.float32),  # Variable number of landmarks, each with x, y, z
            'phrase': tf.io.FixedLenFeature([], tf.string),
            'context': tf.io.FixedLenFeature([], tf.string)
        }

    def __del__(self):
        """
        Destructor method that cleans up resources when the instance is deleted.
        If the `converter` attribute is not `None`, it deletes the `converter` 
        instance to release memory and sets `self.converter` to `None`.
        """
        if self.converter is not None:
            del self.converter
            self.converter = None

    def set_shape(self, num_features, channels):
        """
        Updates the shape configuration for features and channels.

        Args:
            num_features (int): The number of features per sample.
            channels (int): The number of channels per feature (e.g., x, y, z coordinates).

        Sets:
            self.num_features (int): Updates the number of features.
            self.channels (int): Updates the number of channels.
            self.total_num_features (int): Calculates and sets the total number of features,
                                           which is `num_features * channels`.
        """
        self.num_features = num_features
        self.channels = channels
        self.total_num_features = num_features * channels

    def set_input_file(self, input_file):
        """
        Sets the TFRecord file path and updates the file pattern.

        Args:
            input_file (str): Path to a single TFRecord file.

        Sets:
            self.input_file (str): Updates the path to the TFRecord file.
            self.file_pattern (list): Sets `file_pattern` to a list containing the `input_file`.
        """
        self.input_file = input_file
        self.file_pattern = [self.input_file]

    def set_tfrecord_path(self, tfrecord_path):
        """
        Sets the TFRecord directory path and updates the file pattern.

        Args:
            tfrecord_path (str): Path to the directory containing TFRecord files.

        Sets:
            self.input_path (str): Updates the path to the directory containing TFRecord files.
            self.file_pattern (str): Sets the `file_pattern` to match all TFRecord files 
                                      in the specified directory.
        """
        self.input_path = tfrecord_path
        self.file_pattern = f'{tfrecord_path}/*.tfrecord'

    def serialize_tfrecord(self, frame, landmark, phrase, context):
        if isinstance(phrase, float):
            phrase = str(phrase)
        # Ensure landmarks are passed correctly as a flat list (if it's already flat, no need to flatten)
        if isinstance(landmark, list):
            if not isinstance(landmark[0], (int, float)):
                # Ensure landmarks are a NumPy array and flatten them
                landmark = np.array(landmark).flatten()  # Convert to NumPy array and flatten
                self.logger.debug(f"serialize_tfrecord::Flattened landmarks length: {len(landmark)}")
        # Check for zeroed-out or incorrect data

        feature = {
            'frame': tf.train.Feature(int64_list=tf.train.Int64List(value=[frame])),
            'landmark': tf.train.Feature(float_list=tf.train.FloatList(value=landmark)),
            'phrase': tf.train.Feature(bytes_list=tf.train.BytesList(value=[phrase.encode('utf-8')])),
            'context': tf.train.Feature(bytes_list=tf.train.BytesList(value=[context.encode('utf-8')]))
        }
        example_proto = tf.train.Example(features=tf.train.Features(feature=feature))
        return example_proto.SerializeToString()

    # def decode_fn(self, serialized_example):
    #     parsed_example = tf.io.parse_single_example(serialized_example, self.feature_description)

    #     # Convert frames and landmarks to dense if they are sparse
    #     frames = parsed_example['frame']
    #     if isinstance(frames, tf.SparseTensor):
    #         frames = tf.sparse.to_dense(frames, default_value=0)

    #     landmarks = parsed_example['landmark']
    #     if isinstance(landmarks, tf.SparseTensor):
    #         landmarks = tf.sparse.to_dense(landmarks, default_value=0.0)

    #     phrase = parsed_example['phrase']
    #     context = parsed_example['context']

    #     return frames, landmarks, phrase, context

    def decode_fn(self, record_bytes):
        schema = {COL: tf.io.VarLenFeature(dtype=tf.float32) for COL in ALL_FEATURE_COLUMNS}
        schema["phrase"] = tf.io.FixedLenFeature([], dtype=tf.string)
        features = tf.io.parse_single_example(record_bytes, schema)
        phrase = features["phrase"]
        landmarks = ([tf.sparse.to_dense(features[COL]) for COL in ALL_FEATURE_COLUMNS])
        # Transpose to maintain the original shape of landmarks data.
        landmarks = tf.transpose(landmarks)
        print('landmarks : ', landmarks.shape)
        
        return landmarks, phrase


    def get_files(self):
        return self.input_file

    def get_dataset(self, input_file):
        if self.converter is not None:
            if isinstance(input_file, str):
                input_file = [input_file]
            # Create a TFRecord dataset directly in memory
            raw_dataset = self.converter.create_tfrecord_dataset(input_file)
        else:
            raw_dataset = tf.data.TFRecordDataset(input_file)

        # decode usinf self.feature_descriptions
        dataset = raw_dataset.map(self.decode_fn, num_parallel_calls=tf.data.AUTOTUNE)
        
        return dataset

    def write_dataset_to_tfrecord(self, train_ds, tfrecord_path):
        """
        Saves the dataset to the specified path using the updated tf.data.Dataset.save method.
    
        Args:
            train_ds (tf.data.Dataset): The dataset to be saved.
            tfrecord_path (str): The path where the dataset should be saved.
        """
        # Save the dataset using the new tf.data.Dataset.save method
        train_ds.save(tfrecord_path)
        print(f"Dataset saved to {tfrecord_path}")
    
    def read_tfrecord_to_dataset(self, tfrecord_path):
        """
        Loads the dataset from the specified path using the updated tf.data.Dataset.load method.
    
        Args:
            tfrecord_path (str): The path where the dataset is saved.
    
        Returns:
            tf.data.Dataset: The loaded dataset.
        """
        # Load the dataset using the new tf.data.Dataset.load method
        dataset = tf.data.Dataset.load(tfrecord_path)
    
        # Iterate over the dataset to print shapes
        for landmark, target, label in dataset.take(1):  # Take one batch to show shapes
            print(f"Landmark shape: {landmark.shape}, Target shape: {target.shape}, Label shape: {label.shape}")
    
        return dataset
