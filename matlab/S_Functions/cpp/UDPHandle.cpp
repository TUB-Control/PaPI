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

UDPHandle::UDPHandle(int local_port, int remote_port) {
    this->local_port = local_port;
    this->remote_port = remote_port;
    this->remote_host = "127.0.0.1";
}

void UDPHandle::openUDPServer() {
    this->io_service = new boost::asio::io_service();
    this->udp_endpoint = new udp::endpoint(udp::v4(), this->local_port);
    this->udp_socket = new udp::socket(*io_service, *this->udp_endpoint);

    this->udp_endpoint_destination = new udp::endpoint(
        boost::asio::ip::address::from_string(this->remote_host), this->remote_port);


    this->io_service->run();

    this->startRecieve();

}

void UDPHandle::startRecieve() {
    this->udp_socket->async_receive_from(
            boost::asio::buffer(recv_buffer_), *this->udp_endpoint,
            boost::bind(&UDPHandle::handleRecieve, this,
                boost::asio::placeholders::error,
                boost::asio::placeholders::bytes_transferred));
}

void UDPHandle::startSend(int* stream, int msg_length) {
    // printf("UDPHandle::startSend [msg_length]=%d \n", msg_length);
    //
    // for(int i=0; i<27;i++) {
    //     printf("Stream[%d]=%d\n",i, stream[i] );
    // }

    this->udp_socket->async_send_to(
        boost::asio::buffer(stream, msg_length), *this->udp_endpoint_destination,
        boost::bind(&UDPHandle::handleSend, this,
            boost::asio::placeholders::error,
            boost::asio::placeholders::bytes_transferred));
}


void UDPHandle::handleRecieve(const boost::system::error_code& error, std::size_t msg_length/*bytes_transferred*/) {

    if (!error)
    {
        if(this->otherHandleRecieve) {
            this->otherHandleRecieve(msg_length, this->recv_buffer_);
        }

        this->startRecieve();
    }

    if (error == boost::asio::error::message_size) {
        printf("%s\n", "Message longer than buffer");
        this->startRecieve();
    }
}

void UDPHandle::handleSend(const boost::system::error_code& error, std::size_t)
  {
    //   if(error) {
    //       printf("%s\n", "Message could not be sent.");
    //   } else {
    //       printf("%s\n", "Message could be sent.");
    //   }
  }

void UDPHandle::run() {
    printf("%s\n", "UDPHandle::run()" );
    this->thread = new boost::thread(boost::bind(&UDPHandle::openUDPServer, this));
}

void UDPHandle::stop() {
    if (this->thread->joinable()) {
        this->io_service->stop();
        this->thread->join();
    }
}
