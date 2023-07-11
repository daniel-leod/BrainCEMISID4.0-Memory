class Memory:
    def __init__(self, factor):
        self.factor = factor
        self.life_history = {}
        self.life_episode = {}
        self.stats = {}

    def add_memory(self, event, sense, neuron_number, pattern_list=None):
        new_memory = {
            'event': event,
            'sense': sense,
            'neuron_number': neuron_number,
            'pattern_list': pattern_list,
            'linked_to': []
        }

        if pattern_list is not None:
            for pattern in pattern_list:
                if pattern is not None:
                    memory = self.life_history.get(pattern)
                    if memory is not None and memory['pattern_list'] is not None:
                        memory['linked_to'].append(event)

        # Cancion -> pattern_list: [Agrado]
        # Tesis -> pattern_list: [Cancion]
        # Cancion -> pattern_list: [Agrado], linked_to: [Tesis]

        # Pelicula -> pattern_list: [Tesis]
        # Tesis -> pattern_list: [Cancion], linked_to: [Pelicula]

        # Tesis, Pelicula, Cancion, Agrado

        self.stats.setdefault(sense, {'number_registers': 0})
        self.stats[sense]['number_registers'] += 1
        self.life_history[event] = new_memory

    def fill_life_episode(self, event, sense, neuron_number, pattern_list):
        life_episode = {
            'event': event,
            'sense': sense,
            'neuron_number': neuron_number,
            'pattern_list': pattern_list
        }

        self.stats[sense]['number_occurrences'] = 0
        for key, values in self.life_history.items():
            if values['pattern_list'] is not None and event in values['pattern_list']:
                self.stats[sense]['number_occurrences'] += 1

        self.life_episode[event] = life_episode

    def update_memory(self, event, pattern):
        # What about if multiple patterns are linked to that memory??? 🤔
        self.life_history[event]['pattern_list'] = [pattern]

    def handle_attention(self, memory_sequence, pattern=None):
        new_event_key = memory_sequence.split(',')[0]
        new_event = self.life_episode.get(new_event_key, None)

        # handle bidirectional memories

        if self.life_history.get(new_event_key, None) is None and new_event is not None:
            self.add_memory(**new_event)

            if pattern is not None:
                self.update_memory(event=new_event['event'], pattern=pattern)

        elif self.life_history.get(new_event_key) is not None and pattern is not None:
            self.update_memory(event=new_event_key, pattern=pattern)

    def get_memory_sequence(self, sense):
        event = next((value for value in self.life_episode.values() if value['sense'] == sense), None)
        memory_sequence = []

        if event:
            # let's say an event exists in life_history, would it have the same patterns?
            element = self.life_history.get(event['event']) or event

            memory_sequence.append(element['event'])
            for pattern in element['pattern_list']:
                memory = self.life_history.get(pattern, None)
                self._traverse_memory(memory=memory, memory_sequence=memory_sequence)

        return memory_sequence

    def _traverse_memory(self, memory: dict, memory_sequence: list):
        memory_sequence.append(memory['event'])

        if self.life_history[memory['event']]['pattern_list'] is None:
            return

        for pattern in memory['pattern_list']:
            self._traverse_memory(self.life_history[pattern], memory_sequence)

    def get_stats(self):
        return self.stats

    def get_all(self):
        return self.life_history


class History:
    def __init__(self):
        self.memories = {
            'biological': Memory('biological'),
            'emotional': Memory('emotional'),
            'cultural': Memory('cultural')
        }

    def get_memory_sequences(self, params: dict):
        memory_sequence_by_sense = {}

        for sense, sense_params in params.items():
            memory_sequence = {}
            for memory_type, memory_instance in self.memories.items():
                suffix = None
                if sense_params[memory_type] == 1:
                    memory_sequence[memory_type] = memory_instance.get_memory_sequence(sense)

            memory_sequence_by_sense[sense] = memory_sequence

        return memory_sequence_by_sense

    def add_pattern(self, event, sense, neuron_number, pattern_list=None):
        memory_type = self.get_memory_type(event)
        if memory_type is None:
            raise ValueError("Invalid pattern.")

        memory = self.memories[memory_type]
        event_without_suffix = event.rstrip('_bce')
        memory.add_memory(event_without_suffix, sense, neuron_number, pattern_list)

    def add_memory(self, event, sense, neuron_number, pattern_list=None):
        for memory_type, memory_instance in self.memories.items():
            memory_instance.add_memory(event, sense, neuron_number, pattern_list)

    @staticmethod
    def get_memory_type(event):
        suffix_map = {
            '_b': 'biological',
            '_e': 'emotional',
            '_c': 'cultural'
        }

        for suffix, memory_type in suffix_map.items():
            if event.endswith(suffix):
                return memory_type

        return None

    def fill_life_episode(self, event, sense, neuron_number, pattern_list=None):
        for memory_type, memory_instance in self.memories.items():
            memory_instance.fill_life_episode(event, sense, neuron_number, pattern_list)

    def handle_attention(self, factor, memory_sequence, pattern=None):
        memory_instance = self.memories.get(factor)
        memory_instance.handle_attention(memory_sequence, pattern)

    def get_stats(self):
        stats = {}
        for memory_type, memory_instance in self.memories.items():
            stats[memory_type] = memory_instance.get_stats()

        return stats

h = History()
b = h.memories.get('biological')

h.add_pattern(event='Agrado_b', sense='sight', neuron_number=1)
h.add_pattern(event='Agrado_e', sense='sight', neuron_number=89)
h.add_memory(event='Cancion', sense='sight', neuron_number=2, pattern_list=['Agrado'])
h.add_memory(event='Tesis', sense='sight', neuron_number=3, pattern_list=['Cancion'])
h.fill_life_episode(event='Pelicula', sense='sight', neuron_number=9, pattern_list=['Tesis'])
h.handle_attention('biological', 'Pelicula,Tesis,Cancion')
h.handle_attention('emotional', 'Pelicula,Tesis,Cancion')

print(h.get_stats())
print(b.get_all())

MEMORIES = {
    'hearing': {
        'biological': 1,
        'cultural': 1,
        'emotional': 1
    },
    'touch': {
        'biological': 1,
        'cultural': 1,
        'emotional': 0
    },
    'sight': {
        'biological': 1,
        'cultural': 0,
        'emotional': 0
    },
    'smell': {
        'biological': 1,
        'cultural': 0,
        'emotional': 0
    },
    'taste': {
        'biological': 1,
        'cultural': 0,
        'emotional': 0
    },
}

print(h.get_memory_sequences(MEMORIES))
