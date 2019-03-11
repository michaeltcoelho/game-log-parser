# Quake log parser

## Luizalabs challenge

### Proposed Solution

Two packages are provided, the first one is `game`, which provides domain entities and abstract classes, 
and the second one is `parser` which is the concrete implementation of the game's log parser.

The `parser.LogParser` is responsible for reading the log file and to interpret the type of event
by applying a regex expression to each line in the log file.
When an event type is matched then the log parser will notify all event handlers registered to the `games.events.EventObservable` instance, which are
instested in that event type notified. We have event handlers like:
- `parser.handlers.InitGameEventHandler`: responsible for handling `InitGame` events;
- `parser.handlers.ShutdownGameEventHandler`: responsible for handling `ShutdownGame` events, and;
- `parser.handlers.KillEventHandler`: responsible for handling `Kill` events.

For providing persistency for entities it's been choosen the `Repository` Pattern.
We have a concrete implementation of `game.games.GameRepository` in `parser.repositories.MemoryGameRepository` 
whose role is to persist information in memory by making use of a dictionary.

### Requirements

* Python 3.7.1.
* An activated python virtualenv.

#### Considering you have already installed the requirements:

### Installing

Clone the repository and install it:

```bash
git clone https://github.com/michaeltcoelho/game-log-parser.git
```

Go to `/game-log-parser` directory:

Run the following command for installing dependencies:

```bash
make install
```

### Testing

Running tests:

```bash
make test
```

### Running

Running server:

```bash
make server
```
