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

#include <cstdio>

#include <boost/thread.hpp>
#include <boost/asio.hpp>
#include <boost/array.hpp>
#include <boost/signals2.hpp>



class UDPHandle {
private:

    //Thread
    boost::thread* thread;
    bool threadInitialized;

    //Buffer and buffer information
    std::size_t send_msg_length_;
    boost::array<char, 8192> recv_buffer_;
    int* send_buffer_;
    boost::mutex mutex_send_buffer_;


    boost::mutex mutex_starting_thread;
    boost::condition_variable cond_started_thread;

    //Internal communcication
    boost::signals2::signal<void ()> sigSendData;

    //Network stuff
    boost::asio::ip::udp::socket* udp_socket;
    boost::asio::ip::udp::endpoint* udp_endpoint;
    boost::asio::ip::udp::endpoint* udp_endpoint_destination;
    boost::asio::io_service* io_service;
    int local_port;
    int remote_port;
    std::string remote_host;
    std::string local_host;

    void openUDPServer();
    void startRecieve();
    void handleRecieve(const boost::system::error_code& error, std::size_t);
    void handleSend(const boost::system::error_code& error, std::size_t);
    void startSend();

public:
    UDPHandle(int local_port, int remote_port, std::string local_host, std::string remote_host);

    //other handle called when defined
    boost::function<void(std::size_t, boost::array<char, 8192>)> otherHandleRecieve;

    void run();
    void stop();
    void sendData(int*, std::size_t);

};

#endif /* _UDP_HANDLE_ */
