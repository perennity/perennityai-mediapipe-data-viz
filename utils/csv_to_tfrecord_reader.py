import sys
import pandas as pd
import numpy as np
import tensorflow as tf
from .csv_handler import CSVHandler

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


class CSVtoTFRecordConverter:
    def __init__(self, encoding='', logger=None):
        self.logger=logger
        self.csv = CSVHandler(encoding=encoding)

    def csv_to_tfrecord_generator(self, csv_files):
        # List CSV files in memory and convert to a generator of serialized TFRecords
        for csv_file in csv_files:
            df = self.csv.read_csv_file(csv_file)

            # Remove the 'frame', 'phrase', 'context' columns to extract the landmarks
            landmarks = df.drop(['frame', 'phrase', 'context'], axis=1)
            landmarks = landmarks.astype(np.float32)
            landmarks = landmarks.values

            for i, row in df.iterrows():
                yield self.serialize_example(row['frame'], landmarks[i], row['phrase'], row['context'])

    def serialize_example(self, frame, landmarks, phrase, context):
        feature = {
            'frame': self._int64_feature(frame),
            'landmark': self._float_feature(landmarks),  # Assuming landmarks are in 1629 columns
            'phrase': self._bytes_feature(phrase),
        }
        example_proto = tf.train.Example(features=tf.train.Features(feature=feature))
        return example_proto.SerializeToString()

    def _int64_feature(self, value):
        return tf.train.Feature(int64_list=tf.train.Int64List(value=[value]))

    def _float_feature(self, value):
        return tf.train.Feature(float_list=tf.train.FloatList(value=value))

    def _bytes_feature(self, value):
        if isinstance(value, str):  # Check if the value is a string
            return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value.encode()]))
        elif isinstance(value, int):  # If it's an integer, convert it to string first
            return tf.train.Feature(bytes_list=tf.train.BytesList(value=[str(value).encode()]))
        else:
            raise ValueError(f"Unsupported type {type(value)} for _bytes_feature. Only strings and ints are supported.")


    def create_tfrecord_dataset(self, csv_files):
        """
        Create a TFRecord dataset from CSV files.
        :param csv_files: List of paths to CSV files.
        :return: tf.data.Dataset
        """
        return tf.data.Dataset.from_generator(
            lambda: self.csv_to_tfrecord_generator(csv_files),
            output_signature=tf.TensorSpec(shape=(), dtype=tf.string)
        )
