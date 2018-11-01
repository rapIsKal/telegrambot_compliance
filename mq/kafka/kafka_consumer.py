# coding: utf-8

import os
import time
import uuid


import logging
from confluent_kafka.cimpl import Consumer, KafkaError, KafkaException

from mq.kafka.base_kafka_consumer import BaseKafkaConsumer


class KafkaConsumer(BaseKafkaConsumer):
    def __init__(self, config, logger):
        self._config = config["consumer"]
        conf = self._config["conf"]
        conf.setdefault("group.id", str(uuid.uuid1()))
        self.autocommit_enabled = conf.get("enable.auto.commit", True)
        self._logger = logger
        internal_log_path = self._config.get("internal_log_path")
        if internal_log_path:
            debug_logger = logging.getLogger("debug_consumer")
            timestamp = time.strftime("_%d%m%Y_")
            debug_logger.addHandler(logging.FileHandler("{}/kafka_consumer_debug{}{}.log".format(internal_log_path, timestamp, os.getpid())))
            conf["logger"] = debug_logger
        self._consumer = Consumer(**conf)

    def subscribe(self, topics=None):
        topics = topics or list(self._config["topics"].values())
        self._consumer.subscribe(topics)

    def poll(self):
        msg = self._consumer.poll(self._config["poll_timeout"])
        if msg is not None:
            err = msg.error()
            if err:
                if err.code() == KafkaError._PARTITION_EOF:
                    return None
                else:
                    self._logger.info(
                        "KafkaConsumer Error {} at pid {}:  topic={} partition=[{}]  reached end at offset {}\n".format(
                            err.code(),
                            os.getpid(), msg.topic(), msg.partition(),
                            msg.offset()))
                    raise KafkaException(err)

            if msg.value():
                return msg

    def commit_offset(self, msg):
        if msg is not None:
            if self.autocommit_enabled:
                self._consumer.store_offsets(msg)
            else:
                self._consumer.commit(msg, async=False)

    def close(self):
        self._consumer.close()
