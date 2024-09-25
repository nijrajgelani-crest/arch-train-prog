# Simple Process Scheduler

## Setup
### Install requirements

Requires Python 3.10.9.

```
> pip install -r requirements
```

## Usage
### Start the service
```
> ./main.py start
```

### Stop the service
```
> ./main.py stop
```


### Check the status
```
> ./main.py status
```

### Schduling a task

Update the `schedules.json` file. Add the following object to the `schedules` 
list.

```
{
    "at": "2024-12-12 00:00:00+00:00",
    "command": "<command to execute>"
}
```

Completed tasks will be indicated by the `completed` key. For example:
```
{
    "at": "2024-12-12 00:00:00+00:00",
    "command": "<command to execute>",
    "completed": true
}
```