#!/bin/bash

unknown='unknown'
os=$unknown
platform=$unknown
linux='linux'
redhat='redhat'
ubuntu='ubuntu'
darvin='darvin'

ostype=$OSTYPE

export LANG="en_US.UTF-8" \
    LANGUAGE="en_US.UTF-8" \
    LC_ALL="en_US.UTF-8" \
    TZ="Europe/Moscow" \
    TERM="xterm"

if [[ $ostype == *"inux"* ]]; then
   os="$(awk -F= '/^NAME/{print $2}' /etc/os-release)"
   platform=$linux

   echo -e "\n/usr/local/lib\n" >> /etc/ld.so.conf && \
   ldconfig && \

   if [[ $os == *"Red Hat"*  ]]; then
     os=$redhat
   fi
   if [[ $os == *"buntu"*  ]]; then
     os=$ubuntu
   fi
elif [[ $ostype == *"darwin"* ]]; then
   platform=$darvin
   os=$darvin
fi

if [[ $os == $unknown ]]; then
 echo "Error: OS platform is Unknown"
 exit 1
fi


if [[ $os == $redhat ]]; then
 echo "OS is Red Hat"
 yum clean all && \
 rm -rf /var/cache/yum && \
 yum -y --disablerepo=rhel-7-server-rt-beta-rpms install yum-utils && \
 yum-config-manager --disable \* &> /dev/null && \
 yum-config-manager --enable rhel-7-server-rpms && \
 yum-config-manager --enable rhel-7-server-optional-rpms && \
 yum-config-manager --enable rhel-7-server-extras-rpms && \
 yum clean all && \
 rm -rf /var/cache/yum && \
 yum -y update && \
 yum -y install make automake gcc openssl-devel bzip2-devel zlib-devel gcc-c++ libmemcached libmemcached-devel xz-devel unzip
fi


if [[ $os = $ubuntu ]]; then
    apt-get update && \
    apt-get install curl make automake gcc openssl libmemcached-dev zlib1g-dev libssl-dev python3-dev build-essential bzip2 unzip xz-utils python python3.6 python3-distutils && \
    curl https://bootstrap.pypa.io/get-pip.py | python3.6 && \
    pip3.6 install pylibmc && \
    pip install pybind11
    pip3.6 install pybind11
fi

    curl -sL https://github.com/edenhill/librdkafka/archive/adminapi.zip -o /tmp/librdkafka.zip && \
    cd /tmp && \
    unzip -q librdkafka.zip && \
    cd librdkafka-adminapi && \
    ./configure && \
    make && \
    make install && \

    curl -sL https://github.com/confluentinc/confluent-kafka-python/archive/adminapi.zip -o /tmp/confluent-kafka-python.zip && \
    cd /tmp && \
    unzip -qo confluent-kafka-python.zip && \
    cd confluent-kafka-python-adminapi && \
    export C_INCLUDE_PATH=/usr/local/include && \
    export LIBRARY_PATH=/usr/local/lib/lib && \
    python3 setup.py build && \
    python3 setup.py install