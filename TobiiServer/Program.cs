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

        static void Main(string[] args)
        {
            _logger.Info("Starting TobiiLogger...");

            var host = new EyeXHost();
            host.Start();

            var stream = host.CreateGazePointDataStream(GazePointDataMode.LightlyFiltered);
            stream.Next += HandleGazePoint;

            _server = new Server();
            _server.Serve();

            _logger.Info("Exiting TobiiLogger...");

            _server.Close();
            stream.Dispose();
            host.Dispose();
        }

        public static void HandleGazePoint(object sender, GazePointEventArgs e)
        {
            _logger.Trace("GazePointEvent: X: {0} Y: {1} TIMESTAMP: {2}", e.X, e.Y, e.Timestamp);
            _server.Broadcast(JsonConvert.SerializeObject(e));
        }
    }

}
