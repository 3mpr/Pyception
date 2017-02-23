using EyeXFramework;
using Tobii.EyeX.Framework;
using NLog;
using Newtonsoft.Json;

namespace TobiiLogger
{
    class Program
    {
        static private Logger _logger = LogManager.GetCurrentClassLogger();

        static private Server _server;

        /**
         *  The Program entrypoint. Set ups the EyeX objects and their handlers,
         *  the udp server and start the logic.
         */
        static void Main(string[] args)
        {
            _logger.Info("Starting TobiiLogger...");

            var host = new EyeXHost();
            host.Start();

            var gaze_stream = host.CreateGazePointDataStream(GazePointDataMode.LightlyFiltered);
            // var fixation_stream = host.CreateFixationDataStream(FixationDataMode.Sensitive);

            gaze_stream.Next += HandleGazePoint;
            // fixation_stream.Next += handleFixationPoint;

            _server = new Server();
            _server.Serve();

            _logger.Info("Exiting TobiiLogger...");

            _server.Close();
            gaze_stream.Dispose();
            host.Dispose();
        }

        public struct Point {
            public string Name;
            public double X;
            public double Y;
            public double Timestamp;

            public Point(string name, double x, double y, double timestamp)
            {
                this.Name = name;
                this.X = x;
                this.Y = y;
                this.Timestamp = timestamp;
            }

            public Point(GazePointEventArgs e)
            {
                this.Name = "gaze";
                this.X = e.X;
                this.Y = e.Y;
                this.Timestamp = e.Timestamp;
            }

            public Point(FixationEventArgs e)
            {
                this.Name = "fixation";
                this.X = e.X;
                this.Y = e.Y;
                this.Timestamp = e.Timestamp;
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
            _server.Broadcast(JsonConvert.SerializeObject(data));
        }
    }
}
