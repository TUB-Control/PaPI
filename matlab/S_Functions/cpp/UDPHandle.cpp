/*
Copyright (C) 2015 Technische Universität Berlin,
Fakultät IV - Elektrotechnik und Informatik,
Fachgebiet Regelungssysteme,
Einsteinufer 17, D-10587 Berlin, Germany

This file is part of PaPI.

PaPI is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PaPI is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with PaPI.  If not, see <http://www.gnu.org/licenses/>.

Contributors:
Sven Knuth
*/

#include "UDPHandle.hpp"

using boost::asio::ip::udp;

UDPHandle::UDPHandle(int local_port, int remote_port, std::string local_host, std::string remote_host) {
    this->local_port = local_port;
    this->remote_port = remote_port;
    this->remote_host = remote_host;

    //printf("%s\n", this->remote_host.c_str() );
    this->threadInitialized = false;


}

void UDPHandle::handleNewData() {
    int msg_length = this->send_msg_length_;

//    printf("UDPHandle::handleNewData to send(%d) \n", msg_length);

    this->startSend();


}

void UDPHandle::openUDPServer() {
    this->io_service = new boost::asio::io_service();
    this->udp_endpoint = new udp::endpoint(udp::v4(), this->local_port);

    this->udp_endpoint_destination = new udp::endpoint(
        boost::asio::ip::address::from_string(this->remote_host),
        this->remote_port);

    try {
        this->udp_socket = new udp::socket(*this->io_service, *this->udp_endpoint);

        this->sigSendData.connect(boost::bind(&UDPHandle::handleNewData, this));
        this->startRecieve();
        this->io_service->run();

        this->threadInitialized = true;
    } catch (...) {
        printf("Address already in USE! [%s:%d] \n", this-> );

        delete this->io_service;
        delete this->udp_endpoint;
        delete this->udp_endpoint_destination;

        delete this->udp_socket;

    }
}

void UDPHandle::startRecieve() {
    //printf("UDPHandle::startRecieve()\n");
    if (this->udp_socket->is_open())
    {
        this->udp_socket->async_receive_from(
                boost::asio::buffer(this->recv_buffer_), *this->udp_endpoint,
                boost::bind(&UDPHandle::handleRecieve, this,
                    boost::asio::placeholders::error,
                    boost::asio::placeholders::bytes_transferred));
    }
}

void UDPHandle::startSend() {
    //boost::mutex::scoped_lock scoped_lock(this->mutex_send_buffer_);
    int msg_length = this->send_msg_length_;

    //printf("UDPHandle::startSend() [msg_length]=%d \n", msg_length);

    if (!this->threadInitialized) {
        return;
    }

    if (this->udp_socket->is_open())
    {

        // this->udp_socket.async_send_to(
        //     boost::asio::buffer(stream, sizeof(int)*msg_length), *this->udp_endpoint_destination, handler);

        boost::system::error_code ignored_error;

        this->udp_socket->send_to(
            boost::asio::buffer(this->send_buffer_, sizeof(int)*this->send_msg_length_) ,
            *this->udp_endpoint_destination, 0, ignored_error
        );
        if (ignored_error) {
            printf("StartSend:: Error occured: %s \n", ignored_error.message().c_str());
        }
    }
}

void UDPHandle::sendData(int* stream, std::size_t    msg_length) {
//    printf("UDPHandle::startSend() [msg_length] \n");

    this->send_buffer_ = new int[msg_length];
    //std::memcpy(&this->send_buffer_[0], stream, sizeof(int)*msg_length);
    this->send_msg_length_ = msg_length;
    this->send_buffer_ = new int[msg_length];

    std::memcpy(&this->send_buffer_[0], stream, sizeof(int)*msg_length);
    this->sigSendData();
}

void UDPHandle::handleRecieve(const boost::system::error_code& error, std::size_t msg_length/*bytes_transferred*/) {
    printf("%s\n", "UDPHandle::handleRecieve()");
    if (!error)
    {
        if(this->otherHandleRecieve) {
            this->otherHandleRecieve(msg_length, this->recv_buffer_);
        }

        this->startRecieve();
    } else {
        printf("Error occured: %s \n", error.message().c_str());
    }

    if (error == boost::asio::error::message_size) {
        printf("%s\n", "Message longer than buffer");
        this->startRecieve();
    }
}

void UDPHandle::handleSend(const boost::system::error_code& error, std::size_t msg_length/*bytes_transferred*/)
{
    if(error) {
        printf("HandleSend:: Error occured: %s \n", error.message().c_str());
    }
}

void UDPHandle::run() {
    this->thread = new boost::thread(boost::bind(&UDPHandle::openUDPServer, this));
}

void UDPHandle::stop() {
    if (this->thread->joinable()) {
        this->io_service->stop();
        this->thread->join();
        this->udp_socket->close();
        this->threadInitialized = false;
    }
}
