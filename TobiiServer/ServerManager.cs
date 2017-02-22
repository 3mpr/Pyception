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
         *  Class constructor.
         */
        public Server(IPAddress ip = null, Int32 port = 0)
        {
            _ip = ip ?? IPAddress.Any;
            _port = (port == 0) ? 4527 : port;

            _ipe = new IPEndPoint(_ip, _port);
            _server = new UdpClient(_ipe);
            _server.Client.ReceiveTimeout = 1000;

            _lastSender = new IPEndPoint(IPAddress.Any, 0);
            _alive = true;
        }

        /* ------------------------------------------------------------------------------------------------- METHODS */

        public void Serve()
        {
            _logger.Info("Server started at {0}...", _ipe.ToString());

            while(_alive) {
                try {
                    byte[] data = _server.Receive(ref _lastSender);
                    string msg = Encoding.UTF8.GetString(data, 0, data.Length);

                    _logger.Debug("Received ´{0}´ from {1}", msg, _lastSender);

                    HandleMessage(msg, _lastSender);
                } catch(SocketException) {
                    _logger.Debug("Timeout reached.");
                }
            }
        }

        public void Send(string message, IPEndPoint ipe)
        {
            byte[] data = Encoding.UTF8.GetBytes(message);
            _server.Send(data, data.Length, ipe);
        }

        public void Subscribe(IPEndPoint ipe)
        {
            _subscribers.Add(ipe);
            Send("OK", ipe);

            _logger.Info(String.Format("Added subscription for {0}", ipe.Address));
        }

        public void UnSubscribe(IPEndPoint ipe)
        {
            bool resiliated = _subscribers.Remove(ipe);
            if(resiliated) {
                Send("OK", ipe);
                _logger.Info(String.Format("Deleted subscription for {0}", ipe.Address));
            }
        }

        public void HandleMessage(string msg, IPEndPoint ipe)
        {
            switch(msg.ToLower())
            {
                case "subscribe":
                    Subscribe(ipe);
                    break;

                case "close":
                    UnSubscribe(ipe);
                    break;

                default:
                    Send("Undefined", ipe);
                    break;
            }
        }

        public void Broadcast(string message)
        {
            foreach(IPEndPoint ipe in _subscribers) {
                Send(message, ipe);
            }
        }

        public void Close()
        {
            _alive = false;
            _server.Close();
        }

        /* ------------------------------------------------------------------------------------------------ MUTATORS */

        public IPEndPoint LastSender
        {
            get { return _lastSender; }
        }

        public bool Alive
        {
            get { return _alive; }
            set { _alive = value; }
        }
    }

}
