# TobiiLogger
Little Tobii EyeTracking Logging Server.    
    
This server is intended for use with Tobii __Gaming__ devices.     
The Analytics API does provide a better fit for Tobii Pro systems. 
    
The server __does not__ log anything by itself but instead broadcasts the information to registered clients.
The information flow is pretty high (roughly 130Hz) and the server will broadcast timestamps, X and Y position through UDP in realtime __without any attempts to know wheter the clients got the information or not__.

To register to the information flux, send a _"register"_ message to the server on port 4527 (by default).    
You can find a client example [here](https://github.com/3mpr/TobiiLogger/blob/master/TobiiServer/OpenSesame/script.py).

## Usage
1. Download the Tobii EyeTracking _Gaming_ Drivers [here](https://tobiigaming.com/getstarted/).
2. Do the usual `git clone <x>` || `git init && git remote add origin <x>` __or__ download an artefact [here]().
3. Build the solution (skip this step if you downloaded the artefact).
4. Start TobiiLogger.exe.
5. Register your client.
