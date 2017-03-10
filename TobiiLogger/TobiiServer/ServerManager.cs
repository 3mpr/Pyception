using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using NLog;
using System.Collections.Generic;

namespace TobiiLogger
{
    public class Server
    {
        static private Logger _logger = LogManager.GetCurrentClassLogger();

        protected IPAddress _ip;
        protected Int32 _port;
        protected IPEndPoint _ipe;
        protected UdpClient _server;
        protected IPEndPoint _lastSender;

        protected List<IPEndPoint> _subscribers = new List<IPEndPoint>();

        protected bool _alive;

        /* -------------------------------------------------------------------------------- CONSTRUCTOR & DESTRUCTOR */

        /**
         * Class constructor.
         * Set up the ip, the port and the timeout.
         * 
         * @param IPAddress ip      The interface ip to bind to
         * @param Int32     port    The port to bind to
         */
        public Server(IPAddress ip = null, Int32 port = 0)
        {
            _ip = ip ?? IPAddress.Any;
            _port = (port == 0) ? 4527 : port;

            _ipe = new IPEndPoint(_ip, _port);
            _server = new UdpClient(_ipe);
            _server.Client.ReceiveTimeout = 3000;

            _lastSender = new IPEndPoint(IPAddress.Any, 0);
            _alive = true;
        }

        /* ------------------------------------------------------------------------------------------------- METHODS */

        /**
         *  Server entrypoint. Listen for incoming messages and forward
         *  those to the HandleMessage() method.
         */
        public void Serve()
        {
            _logger.Info("Server started at {0}...", _ipe.ToString());

            while(_alive) {
                try {
                    byte[] data = _server.Receive(ref _lastSender);
                    string msg = Encoding.UTF8.GetString(data, 0, data.Length);

                    _logger.Debug("Received ´{0}´ from {1}", msg, _lastSender);

                    HandleMessage(msg, _lastSender);
                } catch(SocketException e) {
                    if(e.ErrorCode == 10060) {
                        _logger.Debug("Timeout reached.");
                    } else if(e.ErrorCode == 10054) {
                        Deregister(_lastSender);
                        // There is no connection state in UDP, dunno how to fix this... ?
                    } else {
                        _logger.Error("An error occured with the socket!");
                    }
                }
            }
        }

        /**
         * Sends a message to the given ip.
         * 
         * @param string        message The message to send
         * @param IPEndPoint    ipe     The host to contact
         */
        public void Send(string message, IPEndPoint ipe)
        {
            byte[] data = Encoding.UTF8.GetBytes(message);
            _server.Send(data, data.Length, ipe);
        }

        /**
         * Add an host to this object subscribers list for future broadcast.
         * 
         * @param IPEndpoint The host
         */
        public void Register(IPEndPoint ipe)
        {
            _subscribers.Add(ipe);
            Send("OK", ipe);

            _logger.Info("Added subscription for {0}:{1}", ipe.Address, ipe.Port);
        }

        /**
         * Remove an host from this object subscribers list.
         * 
         * @param IPEndpoint The host
         */
        public void Deregister(IPEndPoint ipe)
        {
            bool resiliated = _subscribers.Remove(ipe);
            if(resiliated) {
                Send("OK", ipe);
                _logger.Info("Deleted subscription for {0}:{1}", ipe.Address, ipe.Port);
            }
        }
    
        /**
         * Take action in front of the given message from the given host.
         * 
         * @param string        msg The message to act upon
         * @param IPEndPoint    ipe The sender
         */
        public void HandleMessage(string msg, IPEndPoint ipe)
        {
            switch(msg.ToLower())
            {
                case "start":
                case "register":
                case "subscribe":
                    Register(ipe);
                    break;

                case "unregister":
                case "quit":
                case "exit":
                case "close":
                    Deregister(ipe);
                    break;

                default:
                    Send("Undefined", ipe);
                    break;
            }
        }

        /**
         * Broadcast the given message to every subscriber.
         * 
         * @param string message The message
         */
        public void Broadcast(string message)
        {
            foreach(IPEndPoint ipe in _subscribers) {
                Send(message, ipe);
            }
        }

        /**
         * Stop the server and close the socket.
         */
        public void Close()
        {
            _alive = false;
            _server.Close();
        }

        /* ------------------------------------------------------------------------------------------------ MUTATORS */

        /**
         * _lastSender mutator (readonly).
         */
        public IPEndPoint LastSender
        {
            get { return _lastSender; }
        }

        /**
         * _alive mutators.
         */
        public bool Alive
        {
            get { return _alive; }
            set { _alive = value; }
        }
    }
}
