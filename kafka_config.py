TO_AI_TOPIC = "toAI"
FROM_AI_TOPIC = "fromAI"
KAFKA_SOCKET = "178.140.24.244:9092"

kafka_config = {
    "consumer": {
        "poll_timeout": 1.0,
        "topics": {"compliance": FROM_AI_TOPIC},
        "conf": {
            "bootstrap.servers": KAFKA_SOCKET,
            "session.timeout.ms": 6000,
            "enable.auto.commit": True,
            "group.id": "mygroup",
            "auto.commit.interval.ms": 1000,
            "enable.auto.offset.store": True,
            "default.topic.config": {"auto.offset.reset": "smallest"}
        }
    },
    "publisher": {
        "conf": {"bootstrap.servers": KAFKA_SOCKET,
                 "topic.metadata.refresh.interval.ms": 100000},
        "poll_timeout": 0.01,
        "flush_timeout": 10000,
        "partitions_count": 3,
        "topic": {"compliance": TO_AI_TOPIC}
    }
}
