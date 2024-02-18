import math
import random

"""This is a simple, text based clone of the video game Slay the Spire,
by Mega Crit. It is a turn based game where the user fights enemies by
using a randomised deck of cards representing their possible game
actions. The player draws 5 cards from their deck at the start of each
turn and discards their hand at the end of their turn. If they would
draw a card and their deck is empty, the discard pile is shuffled, and
becomes the draw pile.
"""

class Cards:
    """Each card class has a cost, name, and description attribute, and
    is equipped with a method  play() that takes the player character, a
    target enemy, and the current state of the deck, discard pile, hand,
    and exhaust pile, and returns the updated deck, discard pile, hand
    and exhaust pile after the card is played.

    Each card class also is equipped with a constant TARGETS, depending
    on whether its effect requires a target, and is used to determine
    whether to prompt the user for input in multi-enemy battles.
    """
    pass

class SilentCards(Cards):
    """Structured like this to allow for future implementation of
    different characters, with different card sets.
    """
    pass

class Strike(SilentCards):
 
    TARGETS = True

    def __init__(self):
        self.name = "Strike"
        self.description = "Deal 6 damage."
        self.cost = 1

    def play(self, character, target, deck, disc, hand, exha):
        character.attack(target, 6)
        return deck, disc, hand, exha

class Defend(SilentCards):

    TARGETS = False
    
    def __init__(self):
        self.name = "Defend"
        self.description = "Gain 5 block."
        self.cost = 1

    def play(self, character, target, deck, disc, hand, exha):
        character.add_block(5)
        return deck, disc, hand, exha

class Survivor(SilentCards):

    TARGETS = False

    def __init__(self):
        self.name = "Survivor"
        self.description = "Gain 8 block. Discard a card."
        self.cost = 1

    def play(self, character, target, deck, disc, hand, exha):
        character.add_block(8)
        deck, disc, hand = discard(deck, disc, hand)
        return deck, disc, hand, exha

class Neutralize(SilentCards):

    TARGETS = True

    def __init__(self):
        self.name = "Neutralize"
        self.description = "Deal 3 damage. Apply 1 weak."
        self.cost = 0

    def play(self, character, target, deck, disc, hand, exha):
        character.attack(target, 3)
        target.weak +=1
        print(f"{target.name} gained 1 weak!")
        return deck, disc, hand, exha
    
class Acrobatics(SilentCards):

    TARGETS = False

    def __init__(self):
        self.name = "Acrobatics"
        self.description = "Draw 3 cards. Discard a card."
        self.cost = 1

    def play(self, character, target, deck, disc, hand, exha):
        deck, disc, hand = draw(deck, disc, hand, 3)
        deck, disc, hand = discard(deck, disc, hand)
        return deck, disc, hand, exha
    
class Backflip(SilentCards):

    TARGETS = False

    def __init__(self):
        self.name = "Backflip"
        self.description = "Gain 5 block. Draw 2 cards."
        self.cost = 1

    def play(self, character, target, deck, disc, hand, exha):
        character.add_block(5)
        deck, disc, hand = draw(deck, disc, hand, 2)
        return deck, disc, hand, exha
    




class Being:
    """Includes methods and traits used by both the player character
       and enemies.
    """
    def __init__(self, name, maxhp, hp=0, block=0, strength=0, dexterity=0,
                  focus=0, vulnerable=0, weak=0, frail=0, ritual=0):
        self.name = name
        self.maxhp = maxhp # Maximum hit points.
        self.hp = maxhp # Current hit points.
        # Block lasts 1 turn and serves as a buffer for a beings health.
        self.block = block 
        # A being with x strength will deal x more damage.
        self.strength = strength 
        # A being with x dexterity will gain x more block from cards.
        self.dexterity = dexterity 
        self.focus = focus # Currently unused
        # Vulnerable beings take 50% more damage from attacks.
        self.vulnerable = vulnerable
        # Weak beings deal 25% less attack damage.
        self.weak = weak
        # Frail beings gain 25% less block from cards.
        self.frail = frail
        # A being with x ritual will gain x strength at end of turn.
        self.ritual = ritual
        
    
    def attack(self, target, dmg, combat=True):
        """Used to calculate damage and adjust hp of the target which
        is being attacked by self.

        self
          Being Source of the attack.
        target
          Being target of the attack.
        dmg
          int attack amount, unadjusted for modifiers.
        combat
          Boolean used to determine how to calculate damage, depending
          on if source is in combat.
        """
        if combat:
            # Uses truedmgcalc to adjust dmg according to self and
            # target modifiers.
            dmg = truedmgcalc(self, dmg, target)
        if target.block == 0:
            target.hp -= dmg
            print(f"{self.name} dealt {dmg} damage to {target.name},"
                    f" whose health is now {target.hp}.")
        elif target.block >= dmg:
            target.block = target.block - dmg
            print(f"{target.name}\'s block reduced by {dmg}."
                   f" They have {target.block} block remaining.")
        else:
            damagetaken = dmg - target.block
            target.hp -= damagetaken
            print(f"{target.name}'s block was broken, and took"
                    f" {damagetaken} damage.")
            target.block = 0
        # Checks whether target dies from the attack, and ends the
        # battle if the user dies, or all enemies die.
        check_status(target)

    def add_block(self, amount, card=True):
        """Used to calculate block gained, adjusted for Beings traits.

        self
          Being gaining block.
        amount
          int block amount, unadjusted for modifiers.
        card
          Boolean used to determine how to calculate block, depending
          on if coming from a card source.
        """
        if card==True:
            blockadd = amount + self.dexterity
            if self.frail > 0:
                blockadd = math.floor(blockadd * 0.75)
        self.block += blockadd
        print(f"{self.name} gained {blockadd} block, and now has"
               f" {self.block} block.")


class Character(Being):

    def __init__(self, name, maxhp, hp=0, block=0, strength=0,
                  dexterity=0, focus=0, vulnerable=0, weak=0, frail=0,
                    ritual=0, mana_per_turn=3, starting_hand_size=5):
        super().__init__(name, maxhp, hp, block, strength, dexterity,
                          focus, vulnerable, weak, frail, ritual)
        # User's mana resets to this number at the start of their turn.
        self.mana_per_turn = mana_per_turn
        # A card's cost is subtracted from this number when played.
        self.current_mana = mana_per_turn
        # User draws 5 cards at the start of their turn, and discards
        # all cards at the end of it.
        self.starting_hand_size = starting_hand_size
        self.block = 0

    def start_turn(self, deck, disc, hand, exha):
        """ Performs the actions that happen at the start of the user's
        turn, and returns the new state of the user's deck, discard
        pile, hand and exhaust pile.
        
        self
          Character Current player.
        deck
          List Current character deck.
        disc
          List Current character discard pile.
        hand
          List Current character hand.
        exha
          List Current character exhaust pile.
        """
        self.block = 0
        print(f"{self.name}'s block returned to 0.")
        self.current_mana = self.mana_per_turn
        print(f"{self.name}'s energy reset to 3.")
        deck, disc, hand = draw(deck, disc, hand, self.starting_hand_size)
        return deck, disc, hand, exha
    
    def end_turn(self, deck, disc, hand, exha):
        """ Performs the actions that happen at the end of the user's
        turn, and returns the new state of the user's deck, discard
        pile, hand and exhaust pile.
        
        self
          Character Current player.
        deck
          List Current character deck.
        disc
          List Current character discard pile.
        hand
          List Current character hand.
        exha
          List Current character exhaust pile.
        """
        if self.ritual > 0:
            self.strength += self.ritual
            print(f"{self.name}'s ritual increased their strength by"
                   f" {self.ritual} to {self.strength}.")
        # The following traits decrement at the end of a being's turn.
        if self.weak > 0 :
            self.weak -= 1
            print(f"{self.name}'s weak decreased by 1 to {self.weak}.")
        if self.vulnerable > 0 :
            self.vulnerable -= 1
            print(f"{self.name}'s weak decreased by 1 to {self.weak}.")
        if self.frail > 0 :
            self.frail -= 1
            print(f"{self.name}'s vulnerable decreased by 1 to {self.weak}.")
        deck, disc, hand = discard(deck, disc, hand, len(hand))
        return deck, disc, hand, exha


class Silent(Character):
    """A player character; contains starting traits and deck."""
    def __init__(self, name="Silent", maxhp=77, hp=0, block=0, strength=0,
                  dexterity=0, focus=0, vulnerable=0, weak=0, frail=0,
                    ritual=0, mana_per_turn=3, starting_hand_size=5):
        super().__init__(name, maxhp, hp, block, strength, dexterity,
                          focus, vulnerable, weak, frail, ritual,
                            mana_per_turn, starting_hand_size)
        # Creates starting deck.
        self.deck = [Strike(), Strike(), Strike(), Strike(), Strike(),
                     Defend(), Defend(), Defend(), Defend(), Defend(),
                     Survivor(), Neutralize()]
        






class Enemy(Being):
    """Each Subclass of Enemy represents a type of enemy in the game."""

    def start_turn(self):
        """Resets block of enemies at the start of their turn."""
        self.block = 0

    def end_turn(self):
        """ Performs the actions that happen at the end of an enemy's
        turn.
        
        self
          Enemy Enemy within a battle.
        """
        if self.ritual > 0:
            self.strength += self.ritual
            print(f"{self.name}'s ritual increased their strength by"
                    f" {self.ritual} to {self.strength}.")
        if self.weak > 0 :
            self.weak -= 1
            print(f"{self.name}'s weak decreased by 1 to {self.weak}.")
        if self.vulnerable > 0 :
            self.vulnerable -= 1
            print(f"{self.name}'s weak decreased by 1 to {self.weak}.")
        if self.frail > 0 :
            self.frail -= 1
            print(f"{self.name}'s vulnerable decreased by 1 to {self.weak}.")


class Cultist(Enemy):
    def __init__(self, name="Cultist", maxhp=random.randint(50,56), hp=0,
                  block=0, strength=0, dexterity=0, focus=0, vulnerable=0,
                    weak=0, frail=0, ritual=0):
        super().__init__(name, maxhp, hp, block, strength, dexterity, focus,
                          ritual)

    def action_intent(self, target, turn):
        """Uses the enemy, player character and turn number to determine
        the action an enemy will take this turn, and returns a tuple
        containing a string describing its intent and an index
        associated with that action, later used as an argument for the
        action method.
        
        self
          Enemy
        target
          Character Current player character.
        turn
          int Current turn number.
        """
        if turn == 1:
            return (f"{self.name} intends to buff!\n", 0)
        else:
            attackingfor = truedmgcalc(self, 1, target)
            return (f"{self.name} is going to attack you for"
                     f" {attackingfor} damage!", 1)
        
    def action(self, target, act):
        """Carries out the action associated with the index stored in
        act.

        self
          Enemy
        target
          Character Current player character.
        act
          int Index associated with this turns intent.
        """
        if act == 0:
            self.ritual =+ 5
            print(f"{self.name} gained 5 ritual!\n")
        else:
            attackingfor = truedmgcalc(self, 1, target)
            self.attack(target, 1)

class JawWorm(Enemy):
    def __init__(self, name='Jaw Worm', maxhp=random.randint(40,44), hp=0,
                  block=0, strength=0, dexterity=0, focus=0, vulnerable=0,
                    weak=0, frail=0, ritual=0, lastattack=0, lastlastattack=0):
        super().__init__(name, maxhp, hp, block, strength, dexterity, focus,
                          ritual)
        self.lastattack = lastattack
        self.lastlastattack = lastlastattack

    def action_intent(self, target, turn):
        """The following logic makes Jaw Worm chomp on turn 1, and
        on following turns, has a 45% chance to use bellow, 25% chance
        to use chomp, and 30% chance to use thrash. It also prevents Jaw
        Worm from using chomp twice in a row, bellow twice in a row, or
        thrash thrice in a row.
        """
        chomp = (f"{self.name} is going to attack you for"
                    f" {truedmgcalc(self, 11, target)} damage!", 0)
        thrash = (f"{self.name} is going to block and attack you for"
                   f" {truedmgcalc(self, 7, target)} damage!", 1)
        bellow = (f"{self.name} is going to buff and block!", 2)
        if turn == 1:
            return chomp
        outcome = random.random()
        if self.lastattack == 2:
            if outcome > 0.45:
                return thrash
            else:
                return chomp
        elif self.lastattack == 0:
            if outcome > 0.4:
                return thrash
            else:
                return bellow
        elif self.lastattack == 1 and self.lastlastattack == 1:
            if outcome > 0.64:
                return chomp
            else:
                return bellow
        else:
            if outcome < 0.45:
                return bellow
            elif outcome > 0.75:
                return chomp
            else:
                return thrash

        

    
    def action(self, target, action): # Chomp
        if action == 0:
            self.attack(target, 11)
            self.lastlastattack = self.lastattack
            self.lastattack = 0
        elif action == 1: # Thrash
            self.attack(target, 7)
            self.add_block(5)
            self.lastlastattack = self.lastattack
            self.lastattack = 1
        elif action == 2: # Bellow
            self.strength += 3
            print(f"{self.name} gained 3 strength!")
            self.add_block(6)
            self.lastlastattack = self.lastattack
            self.lastattack = 2






        
def truedmgcalc(source, dmg, target):
    """calculates damage dealt using an attack's base attack value, and
    current traits of the attacker and target.
    
    source
      Being Source of the attack.
    dmg
      int Attack's raw attack value.
    target
      Being Target of the attack.
    """
    truedmg = dmg + source.strength
    if source.weak > 0 and target.vulnerable > 0:
        truedmg = math.floor(truedmg*1.125)
    elif source.weak > 0:
        truedmg = math.floor(truedmg*0.75)
    elif target.vulnerable > 0:
        truedmg = math.floor(truedmg*1.5)
    return truedmg

def check_status(receiver):
     """Used to check if a target has died after receiving damage, and
     ends the game if it's the player, or ends the battle if it's an
     enemy, and all other enemies in the battle are dead.

     receiver
       Being Being that just took damage.
     """
     if receiver.hp <= 0:
         if isinstance(receiver, Character):
            print('Game Over!')
            quit()
         elif isinstance(receiver, Enemy):
             print('You Win!')
             quit()

def print_card_list(lis):
    """Used to print lists of cards for the user to read.

    lis
      List containing Card objects.
    """
    for card in enumerate(lis):
        print(f'{card[0] + 1} : {card[1].name} | cost: {card[1].cost}
               | description: {card[1].description}')
    print('')

def print_being(being):
    """Used to print a beings various stats for the user to read.

    being
      Being whose info is to be displayed. OR
      List list containing beings whose info is to be displayed.
    """
    if type(being) == list:
        for x in enumerate(being):
            print(f"{x[0]+1} | {x[1].name} | HP:{x[1].hp}/{x[1].maxhp}"
                    f" | Block: {x[1].block}", end='')
            if x[1].strength > 0:
                print(f" | Strength: {x[1].strength}", end='')
            if x[1].dexterity > 0:
                print(f" | Dexterity: {x[1].dexterity}", end='')
            if x[1].focus > 0:
                print(f" | Focus: {x[1].focus}", end='')
            if x[1].vulnerable > 0:
                print(f" | Vulnerable: {x[1].vulnerable}", end='')
            if x[1].weak > 0:
                print(f" | Weak: {x[1].weak}", end='')
            if x[1].frail > 0:
                print(f" | Frail: {x[1].frail}", end='')
            if x[1].ritual > 0:
                print(f" | Ritual: {x[1].ritual}", end='')
            print('')
    else:
        print(f"{being.name} | HP:{being.hp}/{being.maxhp} | Block:"
               f" {being.block}", end='')
        if being.strength > 0:
            print(f" | Strength: {being.strength}", end='')
        if being.dexterity > 0:
            print(f" | Dexterity: {being.dexterity}", end='')
        if being.focus > 0:
            print(f" | Focus: {being.focus}", end='')
        if being.vulnerable > 0:
            print(f" | Vulnerable: {being.vulnerable}", end='')
        if being.weak > 0:
            print(f" | Weak: {being.weak}", end='')
        if being.frail > 0:
            print(f" | Frail: {being.frail}", end='')
        if being.ritual > 0:
            print(f" | Ritual: {being.ritual}", end='')
        print('')

def battle(character, enemy):
    """Starts a battle between the player character and a single enemy.
    
    character
      Character current player character.
    enemy
      Enemy an Enemy object."""
    
    # deck is initialized as a randomised ordering of the characters starting
    # deck, as some cards are added to deck temporarily for a single battle.
    deck = random.sample(character.deck, len(character.deck))
    # disc contains the cards currently in the discard pile.
    disc = []
    # hand contains the cards currently in the users hand.
    hand = []
    # exha contains the cards currently in the users exhaust pile.
    exha = []
    # turn represents the current turn number.
    turn = 0
    while True: # Contains battle.
        deck, disc, hand, exha = character.start_turn(deck, disc, hand, exha)
        turn += 1
        print(f"TURN {turn}\n")
        actioninfo = enemy.action_intent(character, turn)
        print_being(enemy) # Prints enemy stats.
        print(actioninfo[0]) # Prints enemy intent.
        print_being(character) # Prints character stats.
        while True: # Contains users turn.
            print("Cards in hand:")
            print_card_list(hand)
            player_action = input("Enter the index of the card to play it, or"
                                   " P to end your turn."
                                f" {character.current_mana} energy remaining.")
            if player_action in ('P','p','pass','Pass'):
                break # Ends the users turn.
            card_index = int(player_action) - 1
            # Checks if given index is smaller than hand size and that
            # its corresponding card's cost is affordable.
            if (0 <= card_index <= len(hand) 
            and character.current_mana >= hand[card_index].cost):
                # Plays chosen card.
                temp = hand.pop(card_index)
                print(f'Played {temp.name}!')
                deck, disc, hand, exha = temp.play(character, enemy, deck,
                                                    disc, hand, exha)
                character.current_mana -= temp.cost
                disc.append(temp)
            else:
                print("Invalid input. Please try again.")

        # End player turn.
        deck, disc, hand, exha = character.end_turn(deck, disc, hand, exha)

        # Start enemy turn.
        enemy.start_turn()
        # Carry out enemy action.
        enemy.action(character, actioninfo[1])
        # End enemy turn.
        enemy.end_turn()
        

def multibattle(character, enemylist):
    """Start a battle between the player character and multiple enemies.
    
    character
      Character current player character.
    enemylist
      List a list containing Enemy objects."""
    
    deck = random.sample(character.deck, len(character.deck))
    disc = []
    hand = []
    exha = []
    turn = 0
    while True:
        # start player turn
        deck, disc, hand, exha = character.start_turn(deck, disc, hand, exha)
        turn += 1
        print(f'TURN {turn}\n')
        print_being(character)
        print()
        actioninfo = []
        for enemy in enemylist:
            actioninfo.append(enemy.action_intent(character, turn))
        for i in range(len(enemylist)):
            print_being(enemylist[i])
            print(actioninfo[i][0])
        while True:
            print('cards in hand:\n')
            print_card_list(hand)
            player_action = input("Enter the index of the card to play it, or "
            f"P to end your turn. {character.current_mana} energy remaining. ")
            if player_action in ('P','p','pass','Pass'):
                break
            card_index = int(player_action) - 1
            if (0 <= card_index <= len(hand)
            and character.current_mana >= hand[card_index].cost):
                temp = hand.pop(card_index)
                if temp.TARGETS == True:
                    print("Select target enemy: ")
                    print_being(enemylist)
                    target = enemylist[int(input())-1]
                print(f"Played {temp.name}!")
                deck, disc, hand, exha = temp.play(character, target, deck,
                                                    disc, hand, exha)
                character.current_mana -= temp.cost
                disc.append(temp)
            else:
                print("Invalid input. Please try again.")
        deck, disc, hand, exha = character.end_turn(deck, disc, hand, exha)
        # End player turn.

        # Start enemy turn.
        for enemy in enemylist:
            enemy.start_turn()
        for enemy in enumerate(enemylist):
            enemy[1].action(character, actioninfo[enemy[0]][1])
        for enemy in enemylist:
            enemy.end_turn()
        # End enemy turn.



def draw(deck, disc, hand, n=1):
    """Draws n cards from the deck and puts them in hand, shuffling disc
    into deck first if deck is empty. Returns the new state of deck,
    discard, and hand.
    
    deck
      List containing card objects.
    disc
      List containing card objects.
    hand
      List containing card objects.
    """
    for i in range(n):
        if deck == [] and disc == []:
            return hand, deck, disc
        elif deck == []:
            deck = random.sample(disc, len(disc))
            disc = []
            hand.append(deck.pop())
        else:
            hand.append(deck.pop())
    return deck, disc, hand

def discard(deck, disc, hand, n=1):
    """Discards n cards from hand and puts them in disc, prompting the
    user to select a card to discard each time unless there is only one
    choice available. Returns new state of deck, disc and hand.
    
    deck
      List containing card objects.
    disc
      List containing card objects.
    hand
      List containing card objects.
    """
    for i in range(n):
        if hand == []:
            return deck, disc, hand
        elif len(hand) <= n:
            disc.extend(hand)
            hand = []
        else:
            print("Which card would you like to discard? ")
            print_card_list(hand)
            disc.append(hand.pop(int(input())-1))
    return deck, disc, hand

silent = Silent()
bird1 = Cultist()
bird2 = JawWorm()
battle(silent, bird2)








