# To set up embodied service on new machine

```
sudo chmod +x /home/olin/VLA_Star/experiments/light_sleep.sh
sudo systemctl daemon-reload
sudo systemctl enable startup-script.service
```

## Testing:
```
sudo systemctl start startup-script.service
```
