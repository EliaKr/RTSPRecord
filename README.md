# RTSPRecord

A simple RTSP stream recorder that records a stream in segments and supports looping the recording once storage space runs out. Ideal for use in low-powered devices like the Raspberry Pi.

## Dependencies

- ffmpeg

## Usage

### Manual Use

1. Clone this repository
2. Add the stream information to the streamlist.json file according to the example. You can add more entries to add more streams to be recorded. Make sure the record directories are accessible by the program.
3. Run RTSPRecord.py

### Use with a system service

1. Clone this repository
2. Add the stream information to the streamlist.json file according to the example. You can add more entries to add more streams to be recorded. Make sure the record directories are accessible by the program.
3. Make RTSPRecord.py executable
` chmod +x /path/to/script/directory/RTSPStream.py `
4. Create a new service
`sudo nano /etc/systemd/system/RTSPRecord.service`

Add the following content to the service file.

```bash
[Unit]
Description=RTSPRecord Service
After=network.target

[Service]
ExecStart=/usr/bin/python3 /path/to/script/directory/RTSPStream.py
WorkingDirectory=/path/to/script/directory
Restart=always
User=youruser
Group=yourgroup

[Install]
WantedBy=multi-user.target
```

5. Reload systemd and enable the service

```bash
sudo systemctl daemon-reload
sudo systemctl enable RTSPRecord.service
sudo systemctl start RTSPRecord.service
```

#### Note: Unencrypted RTSP streams can be easily intercepted. If you want to record a device outside of your local network the best solution is a site-to-site VPN.
