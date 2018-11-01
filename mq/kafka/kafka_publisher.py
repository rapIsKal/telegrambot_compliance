# coding: utf-8
import logging
import time
import os
from confluent_kafka import Producer

from mq.kafka.base_kafka_publisher import BaseKafkaPublisher


class KafkaPublisher(BaseKafkaPublisher):
    def __init__(self, config, logger):
        self._config = config["publisher"]
        self.logger = logger
        conf = self._config["conf"]
        conf["error_cb"] = self._error_callback
        conf["on_delivery"] = self._delivery_callback
        internal_log_path = self._config.get("internal_log_path")
        if internal_log_path:
            debug_logger = logging.getLogger("debug_publisher")
            timestamp = time.strftime("_%d%m%Y_")
            debug_logger.addHandler(logging.FileHandler("{}/kafka_publisher_debug{}{}.log".format(internal_log_path, timestamp, os.getpid())))
            conf["logger"] = debug_logger
        self._producer = Producer(**conf)

    def send(self, value, key=None, topic_key=None):
        try:
            topic = self._config["topic"]
            if topic_key is not None:
                topic = topic[topic_key]
            producer_params = dict()
            if key is not None:
                producer_params["key"] = key
            self._producer.produce(topic=topic, value=value, **producer_params)
        except BufferError as e:
            self.logger.error("KafkaProducer: Local producer queue is full ({} messages awaiting delivery):"
                              " try again\n".format(len(self._producer)))
        self._poll()

    def _poll(self):
        while True:
            result = self._producer.poll(self._config["poll_timeout"])
            if not result:
                return

    def _error_callback(self, err):
        self.logger.error("KafkaProducer: Error: {}".format(err))

    def _delivery_callback(self, err, msg):
        if err:
            message_text = msg.value()
            try:
                message_text = message_text.decode("utf-8")
            except UnicodeDecodeError:
                message_text = "Can't decode: {}".format(message_text)
            self.logger.error("KafkaProducer: Message {} send failed: {}\n".format(message_text, err))

    def close(self):
        self._producer.flush(self._config["flush_timeout"])
