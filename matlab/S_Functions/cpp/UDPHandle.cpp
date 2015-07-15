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

UDPHandle::UDPHandle() {
    this->msg_length = 0;
}

void UDPHandle::openUDPServer() {
    printf("%s\n", "UDPHandle::openUDPServer" );
    this->io_service = new boost::asio::io_service();

    this->udp_endpoint = new udp::endpoint(udp::v4(), 1999);
    this->udp_socket = new udp::socket(*io_service, *this->udp_endpoint);

    this->startRecieve();

    this->io_service->run();

}

void UDPHandle::startRecieve() {
    printf("%s\n", "UDPHandle::startRecieve");
    this->udp_socket->async_receive_from(
            boost::asio::buffer(recv_buffer_), *this->udp_endpoint,
            boost::bind(&UDPHandle::handleRecieve, this,
                boost::asio::placeholders::error,
                boost::asio::placeholders::bytes_transferred));
}


void UDPHandle::handleRecieve(const boost::system::error_code& error, std::size_t msg_length/*bytes_transferred*/) {
    printf("UDPHandle::handleRecieve (msg_length=%zu)\n", msg_length);


    if (!error)
    {
        this->otherHandler(msg_length, this->recv_buffer_);

        this->msg_length = msg_length;
        this->startRecieve();
    }

    if (error == boost::asio::error::message_size) {
        printf("%s\n", "Message longer than buffer");
        this->startRecieve();
    }
}

void UDPHandle::run() {
    printf("%s\n", "UDPHandle::run()" );
    this->thread = new boost::thread(boost::bind(&UDPHandle::openUDPServer, this));
}


void UDPHandle::setBindHandleRecieve(void* member_function, void* object) {
    printf("%s\n", "UDPHandle::setBindHandleRecieve");
}
