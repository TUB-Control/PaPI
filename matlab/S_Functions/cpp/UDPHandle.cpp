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

You should have received a copy of the GNU General Public License
along with PaPI.  If not, see <http://www.gnu.org/licenses/>.

Contributors:
Sven Knuth
*/

#include "UDPHandle.hpp"

using boost::asio::ip::udp;

void displayAndChange(boost::thread& daThread);

/**
    This class is used to create a socket for a given local port.
    A recieved package can be send handle by another function by binding such a function to
    this->otherHandleRecieve

    @param local_port  Local port
    @param remote_port Remote port
    @param local_host  Local network interface
    @param remote_host Remote/Target interface
*/
UDPHandle::UDPHandle(int local_port, int remote_port, std::string local_host, std::string remote_host) {
    this->local_port = local_port;
    this->remote_port = remote_port;

    this->remote_host = remote_host;
    this->local_host  = local_host;

    this->threadInitialized = false;

    this->send_msg_length_ = 0;

}

/**
    This function opens a udp server which is listening on the given port and interface.
    Should be opened in an extra thread.
*/
void UDPHandle::openUDPServer() {
    this->io_service = new boost::asio::io_service();
    this->udp_endpoint = new udp::endpoint(
        udp::v4(),
        this->local_port);

    this->udp_endpoint_destination = new udp::endpoint(
        boost::asio::ip::address::from_string(this->remote_host),
        this->remote_port);

    #ifdef _UDP_HANDLE_DEBUG_
        printf("Local  address:[%s:%d] \n", this->local_host.c_str(), this->local_port);
        printf("Remote address:[%s:%d] \n", this->remote_host.c_str(), this->remote_port);
    #endif

    try {
        #ifdef _UDP_HANDLE_DEBUG_
            printf("%s\n", "Configure Thread");
        #endif

        this->udp_socket = new udp::socket(*this->io_service, *this->udp_endpoint);

        this->sigSendData.connect(boost::bind(&UDPHandle::startSend, this));
        this->startRecieve();

        this->threadInitialized = true;

        #ifdef _UDP_HANDLE_DEBUG_
            printf("%s\n", "notify_all waiting threads");
        #endif

        this->cond_started_thread.notify_all();

        this->io_service->run();
    } catch (...) {
        printf("Address already in USE! [%s:%d] \n", this->local_host.c_str(), this->local_port);
        this->threadInitialized = false;


        // delete this->io_service;
        // delete this->udp_endpoint;
        // delete this->udp_endpoint_destination;
        //
        // delete this->udp_socket;

    }

    this->cond_started_thread.notify_all();

}

/**
    This function is called to triggere the current thread to wait
    for new incoming packages.
*/
void UDPHandle::startRecieve() {

    if (this->udp_socket->is_open())
    {
        this->udp_socket->async_receive_from(
                boost::asio::buffer(this->recv_buffer_), *this->udp_endpoint,
                boost::bind(&UDPHandle::handleRecieve, this,
                    boost::asio::placeholders::error,
                    boost::asio::placeholders::bytes_transferred));
    }
}
/**
    Callback function which gets called if new data were written to the internal send_buffer_.
*/
void UDPHandle::startSend() {
    int msg_length = this->send_msg_length_;

    if (!this->threadInitialized) {
        return;
    }

    if (this->udp_socket->is_open())
    {

        boost::system::error_code ignored_error;
        this->mutex_send_buffer_.lock();
        this->udp_socket->send_to(
            boost::asio::buffer(this->send_buffer_, sizeof(char)*this->send_msg_length_) ,
            *this->udp_endpoint_destination, 0, ignored_error
        );
        this->mutex_send_buffer_.unlock();

        if (ignored_error) {
            printf("StartSend:: Error occured: %s \n", ignored_error.message().c_str());
        }
    }
}

/**
    Public function called to write to the internal buffer.

    @param stream Data stream which should be sent.
    @param msg_length Defines the amount of elements in the data stream
*/
void UDPHandle::sendData(const char* stream, std::size_t msg_length) {
    if (this->threadInitialized) {
        this->send_msg_length_ = msg_length;

        this->mutex_send_buffer_.lock();
        std::memcpy(this->send_buffer_.begin(), stream, sizeof(char)*msg_length);
        this->mutex_send_buffer_.unlock();
        this->sigSendData();
    }
}

void UDPHandle::sendData(int* stream, std::size_t msg_length) {
    if (this->threadInitialized) {
        this->send_msg_length_ = msg_length*4;

        this->mutex_send_buffer_.lock();
        std::memcpy(this->send_buffer_.begin(), stream, sizeof(int)*msg_length);
        this->mutex_send_buffer_.unlock();
        this->sigSendData();

    }
}

/**
    Callback function which is triggered by an incoming package.
    Will also call the this->otherHandleRecieve if defined.
*/
void UDPHandle::handleRecieve(const boost::system::error_code& error, std::size_t msg_length/*bytes_transferred*/) {

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

/**
    Callback function which is triggered by a sent package.
*/
void UDPHandle::handleSend(const boost::system::error_code& error, std::size_t msg_length/*bytes_transferred*/)
{
    if(error) {
        printf("HandleSend:: Error occured: %s \n", error.message().c_str());
    }
}

/**
    This function must be called to start the udp server. Will also start an extra thread
    which will handle all recieved packages.
*/
void UDPHandle::run() {
    #ifdef _UDP_HANDLE_DEBUG_
        printf("UDPHandle::run()\n");
    #endif

    if (!this->threadInitialized) {

        boost::unique_lock<boost::mutex> lock(this->mutex_starting_thread);

        this->thread = new boost::thread(boost::bind(&UDPHandle::openUDPServer, this));

        //TODO: Add root detection
        #if defined(BOOST_THREAD_PLATFORM_WIN32)
            // ... window version
        #elif defined(BOOST_THREAD_PLATFORM_PTHREAD)
            displayAndChange(*this->thread);
        #else
            #error "Boost threads unavailable on this platform"
        #endif

        if ( !this->threadInitialized ) {
            #ifdef _UDP_HANDLE_DEBUG_
                printf("Wait for thread to finish \n");
            #endif
            this->cond_started_thread.wait(lock);
        }
    }

}
/**
    This function must be called to stop the udp server and join the started thread.
*/
void UDPHandle::stop() {
    if (this->threadInitialized) {
        if (this->thread->joinable()) {
            this->io_service->stop();
            this->thread->join();
            this->udp_socket->close();
            this->threadInitialized = false;
        }
    }
}

//*************************************************
//**** Helper functions
//*************************************************

/*
    Was taken from here: http://stackoverflow.com/questions/1479945/setting-thread-priority-in-linux-with-boost
    Minor modification: Set FIFO priority to 'sched_get_priority_max(SCHED_FIFO)'
    Date: 18. Juli 2015

    @param daThread boost::thread which should be manipulated
    @param display Flag which can be set to 'ne 0' to display some thread information
*/
void displayAndChange(boost::thread& daThread)
{

    int retcode;
    int policy;

    pthread_t threadID = (pthread_t) daThread.native_handle();

    struct sched_param param;

    if ((retcode = pthread_getschedparam(threadID, &policy, &param)) != 0)
    {
        errno = retcode;
        perror("pthread_getschedparam");
        exit(EXIT_FAILURE);
    }

    #ifdef _UDP_HANDLE_DEBUG_
            std::cout << "INHERITED: ";
            std::cout << "policy=" << ((policy == SCHED_FIFO)  ? "SCHED_FIFO" :
                                       (policy == SCHED_RR)    ? "SCHED_RR" :
                                       (policy == SCHED_OTHER) ? "SCHED_OTHER" :
                                                                 "???")
                      << ", priority=" << param.sched_priority << std::endl;
    #endif

    policy = SCHED_FIFO;
    param.sched_priority = sched_get_priority_max(SCHED_FIFO);

    if ((retcode = pthread_setschedparam(threadID, policy, &param)) != 0)
    {
        errno = retcode;
        perror("pthread_setschedparam");
        exit(EXIT_FAILURE);
    }

    #ifdef _UDP_HANDLE_DEBUG_
        std::cout << "  CHANGED: ";
        std::cout << "policy=" << ((policy == SCHED_FIFO)  ? "SCHED_FIFO" :
                                   (policy == SCHED_RR)    ? "SCHED_RR" :
                                   (policy == SCHED_OTHER) ? "SCHED_OTHER" :
                                                              "???")
                  << ", priority=" << param.sched_priority << std::endl;
    #endif
}
