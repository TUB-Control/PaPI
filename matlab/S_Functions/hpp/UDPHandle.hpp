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

Source: http://www.boost.org/doc/libs/1_35_0/doc/html/boost_asio/tutorial/tutdaytime6/src.html, 16. Juli 2015
*/

#ifndef _UDP_HANDLE_
#define _UDP_HANDLE_

#include <iostream>
#include <sstream>
#include <cstdio>
#include <stdexcept>

#include <boost/thread.hpp>
#include <boost/asio.hpp>
#include <boost/array.hpp>


class UDPHandle {
private:

    boost::thread* thread;    
    boost::asio::ip::udp::socket* udp_socket;
    boost::asio::ip::udp::endpoint* udp_endpoint;

    boost::asio::ip::udp::endpoint* udp_endpoint_destination;


    boost::array<int, 8192> recv_buffer_;
    boost::asio::io_service* io_service;

    int local_port;
    int remote_port;
    std::string remote_host;

    void openUDPServer();
    void startRecieve();
    void handleRecieve(const boost::system::error_code& error, std::size_t);
    void handleSend( const boost::system::error_code&,
                     std::size_t );
public:
    UDPHandle(int local_port, int remote_port);

    boost::function<void(std::size_t, boost::array<int, 8192>)> otherHandleRecieve;

    void run();
    void stop();

    void startSend(int*, int);

};

#endif /* _UDP_HANDLE_ */
