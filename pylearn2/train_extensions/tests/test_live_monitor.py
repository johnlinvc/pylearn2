import unittest
from nose.tools import assert_raises
import multiprocessing as mp

try:
    import zmq
except:
    raise unittest.SkipTest

from pylearn2.scripts.train import train
import pylearn2.train_extensions.live_monitoring as lm


def train_mlp():
    train('pylearn2/pylearn2/train_extensions/tests/live_monitor_test.yaml')


def test_live_monitoring():
    # Start training an MLP with the LiveMonitoring train extension
    p = mp.Process(target=train_mlp)
    p.start()

    # Query for list of channels being monitored
    correct_result = [
        'train_objective',
        'train_y_col_norms_max',
        'train_y_row_norms_min',
        'train_y_nll',
        'train_y_col_norms_mean',
        'train_y_max_max_class',
        'train_y_min_max_class',
        'train_y_row_norms_max',
        'train_y_misclass',
        'train_y_col_norms_min',
        'train_y_row_norms_mean',
        'train_y_mean_max_class',
        'learning_rate',
        'training_seconds_this_epoch',
        'total_seconds_last_epoch'
    ]
    monitor = lm.LiveMonitor()
    result = monitor.list_channels().data
    assert(result == correct_result)

    # Query for first two elements of train_objective data
    monitor = lm.LiveMonitor()
    monitor.update_channels(['train_objective'], start=0, end=2)
    assert(len(monitor.channels['train_objective'].val_record) == 2)

    # Query for second element of train_objective data
    monitor = lm.LiveMonitor()
    monitor.update_channels(['train_objective'], start=1, end=2)
    assert(len(monitor.channels['train_objective'].val_record) == 1)

    # Close the training process
    p.join()

    # Perform a few sanity checks. Done here because we have a monitor object
    # but we no longer need to interact with the training process which has
    # ended.

    # Test not a list
    assert_raises(
        AssertionError,
        monitor.update_channels,
        0
    )

    # Test empty list
    assert_raises(
        AssertionError,
        monitor.update_channels,
        []
    )

    # Test bad start/end combination
    assert_raises(
        AssertionError,
        monitor.update_channels,
        ['train_objective'], start=2, end=1
    )
