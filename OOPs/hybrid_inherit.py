class Person:

    def __init__(self, name, age):
        self.name = name
        self.age = age

    def introduce(self):
        print(f"My name is {self.name} and I am {self.age} years old.")

    def sleep(self, hours):
        print(f"{self.name} slept for {hours} hours.")

    def show_basic_info(self):
        print(f"Name: {self.name}")
        print(f"Age: {self.age}")


class PartyPerson(Person):

    def __init__(self, name, age, favorite_music, party_frequency):
        super().__init__(name, age)

        self.favorite_music = favorite_music
        self.party_frequency = party_frequency

    def attend_party(self, location):
        print(f"{self.name} is attending a party at {location}.")

    def play_music(self):
        print(
            f"{self.name} is playing "
            f"{self.favorite_music} music."
        )

    def party_info(self):
        print(f"Favorite music: {self.favorite_music}")
        print(f"Party frequency: {self.party_frequency} times/month")


class SadPerson(Person):

    def __init__(self, name, age, mood, reason):
        super().__init__(name, age)

        self.mood = mood
        self.reason = reason

    def show_mood(self):
        print(f"{self.name}'s current mood: {self.mood}")

    def explain_reason(self):
        print(f"Reason for feeling this way: {self.reason}")

    def improve_mood(self):
        print(f"{self.name} is trying to improve their mood.")


class Drinker(PartyPerson, SadPerson):

    def __init__(
        self,
        name,
        age,
        favorite_music,
        party_frequency,
        mood,
        reason,
        drink_preference
    ):

        PartyPerson.__init__(
            self,
            name,
            age,
            favorite_music,
            party_frequency
        )

        SadPerson.__init__(
            self,
            name,
            age,
            mood,
            reason
        )

        self.drink_preference = drink_preference
        self.total_drinks = 0

    def drink(self, quantity):
        self.total_drinks += quantity

        print(
            f"{self.name} had {quantity} drink(s)."
        )

    def show_drinking_info(self):
        print(f"Preferred drink: {self.drink_preference}")
        print(f"Total drinks: {self.total_drinks}")

    def leave_party(self):
        print(
            f"{self.name} has left the party "
            "and is going home."
        )