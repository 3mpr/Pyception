using EyeXFramework;
using Tobii.EyeX.Framework;
using NLog;
using Newtonsoft.Json;
using System;

namespace TobiiLogger
{
    class Program
    {
        static private Logger _logger = LogManager.GetCurrentClassLogger();

        static private Server _server;

        private static Int64 _beginTime;
        private static Int64 _endTime;

        /**
         *  The Program entrypoint. Set ups the EyeX objects and their handlers,
         *  the udp server and start the logic.
         */
        static void Main(string[] args)
        {
            _logger.Info("Starting TobiiLogger...");

            _beginTime = (Int64) (DateTime.UtcNow.Subtract(new DateTime(1970, 1, 1))).TotalSeconds;

            var host = new EyeXHost();
            host.Start();

            var gaze_stream = host.CreateGazePointDataStream(GazePointDataMode.LightlyFiltered);
            // var fixation_stream = host.CreateFixationDataStream(FixationDataMode.Sensitive);

            gaze_stream.Next += HandleGazePoint;
            // fixation_stream.Next += handleFixationPoint;

            _server = new Server();
            _server.Serve();

            _endTime = (Int64)(DateTime.UtcNow.Subtract(new DateTime(1970, 1, 1))).TotalSeconds;
            _logger.Info("Exiting TobiiLogger...");

            _server.Close();
            gaze_stream.Dispose();
            host.Dispose();
        }

        public struct Point {
            public string Name;
            public double X;
            public double Y;
            public string Timestamp;

            public Point(string name, double x, double y, double timestamp)
            {
                this.Name = name;
                this.X = x;
                this.Y = y;
                this.Timestamp = timestamp.ToString();
            }

            public Point(GazePointEventArgs e)
            {
                this.Name = "gaze";
                this.X = e.X;
                this.Y = e.Y;
                this.Timestamp = e.Timestamp.ToString();
            }

            public Point(FixationEventArgs e)
            {
                this.Name = "fixation";
                this.X = e.X;
                this.Y = e.Y;
                this.Timestamp = e.Timestamp.ToString();
            }
        }

        /**
         * React to GazePointEventArgs thrown by the GazePointDataStream
         * and redirect the output to the udp server.
         * 
         * @param object                sender  The data stream
         * @param GazePointEventArgs    e       The event
         */
        public static void HandleGazePoint(object sender, GazePointEventArgs e)
        {
            _logger.Trace("GazePointEvent: X: {0} Y: {1} TIMESTAMP: {2}", e.X, e.Y, e.Timestamp);
            Point data = new Point(e);
            _server.Broadcast(JsonConvert.SerializeObject(data));
        }

        public static void handleFixationPoint(object sender, FixationEventArgs e)
        {
            _logger.Trace("FixationEvent: X:{0} Y: {1} TIMESTAMP: {2}", e.X, e.Y, e.Timestamp);
            Point data = new Point(e);
            data.Timestamp = System.DateTime.Now.ToShortTimeString();
            _server.Broadcast(JsonConvert.SerializeObject(data));
        }

        /**
         * Timestamp correction utility function.
         * 
         * Timestamps provided by the Tobii EyeSDK are arbitrary / relative to each others,
         * it is thus necessary to use a little function to register record beginning and end
         * to provide useful timestamps.
         */
        public void time( double timestamp )
        {
            var time = DateTime.UtcNow;
        }
    }
}
