:- use_module(library(clpfd)).
:- use_module(library(dcg/basics)).


wood('Spruce').
wood('Oak').
wood('Birch').
object('Torch').
object('Plank').
object('Stick').
stone('SandStone').


plank(Type) :- 
	wood(Type).

can_make_from(object('Plank'), object(wood(Type))) :-
	wood(Type).
can_make_from(object('Stick'), object(wood(Type))) :-
	wood(Type).
can_make_from(object('Bowl'), object('Plank')).


make_plank(inventory(Lst), PlankObj, OutInventory) :- 
	PlankObj = object('Plank'),
	can_make_from(PlankObj, SourceObj),
	remove_from_inventory(inventory(Lst), SourceObj, Out1),
	put_to_inventory(Out1, PlankObj, O1),
	put_to_inventory(O1, PlankObj, O2),
	put_to_inventory(O2, PlankObj, O3),
	put_to_inventory(O3, PlankObj, OutInventory).

		 
mine_wood(Inventory, X, Out) :-
	X = object(wood(WoodType)),
	wood(WoodType),
	put_to_inventory(Inventory, X, Out).

mine_stone(Inventory, X, Out) :-
	X = object(stone(StoneType)),
	stone(StoneType),
	put_to_inventory(Inventory, X, Out).

mine(Inventory, Something, OutInv) :- 
	mine_wood(Inventory, Something, OutInv);
	mine_stone(Inventory, Something, OutInv).


make_stick(inventory(Lst), object('Stick'), OutInventory) :-
	can_make_from(object('Stick'), SourceObj),
	remove_from_inventory(inventory(Lst), SourceObj, Out1),
	remove_from_inventory(Out1, SourceObj, Out2),
	put_to_inventory(Out2, object('Stick'), OutInventory).


make_bowl(inventory(Lst), object('Bowl'), OutInventory) :- 
	can_make_from(object('Bowl'), SourceObj1),
	can_make_from(object('Bowl'), SourceObj2),
	can_make_from(object('Bowl'), SourceObj3),
	remove_from_inventory(inventory(Lst), SourceObj1, O1),
	remove_from_inventory(O1, SourceObj2, O2),
	remove_from_inventory(O2, SourceObj3, O3),
	put_to_inventory(O3, object('Bowl'), OutInventory).


make(Inv, Something, Out) :- 
	make_stick(Inv, Something, Out);
	make_plank(Inv, Something, Out);
	make_bowl(Inv, Something, Out).

make_inventory(inventory(Lst)) :-
	Lst = [
	       [],
               [],
               []].

list([])     --> [].
list([L|Ls]) --> [L], list(Ls).	
concatenation([]) --> [].
concatenation([List|Lists]) -->
        list(List),
        concatenation(Lists).

cell_with_item([Head|Tail], object(ObjType), OutCell) :- 
	InCell = [Head|Tail],
	InCell = [object(ObjType)| Tail],
	append(InCell, [object(ObjType)], OutCell),
	length(InCell, L),
	L #< 10.


cell_with_item([], object(ObjType), OutCell) :- 
	OutCell = [object(ObjType)].


put_to_inventory(inventory(Lst), Item, inventory(Lst2)) :-
	Item = object(_),
	member(Cell, Lst),
	cell_with_item(Cell, Item, OutCell),
	phrase(concatenation([H, [Cell], Tail]), Lst),
	phrase(concatenation([H, [OutCell], Tail]), Lst2).


remove_from_inventory(inventory(Lst), Item, inventory(Lst2)) :-
	Item = object(_),
	member(Cell, Lst),
	member(Item, Cell),
	cell_with_item(Without, Item, Cell),
	phrase(concatenation([H, [Cell], Tail]), Lst),
	phrase(concatenation([H, [Without], Tail]), Lst2).


% solved
next_state(Initial, _, EndState, 0) :- 
	Initial = EndState.

% mine something
next_state(Initial, Steps, EndState, Nsteps ) :- 
	0 #< Nsteps,
	LeftSteps #= Nsteps - 1,
	mine(Initial, Something, NewState),
	Steps = [mine(Something)| NewSteps],
	next_state(NewState, NewSteps, EndState, LeftSteps).


% craft something
next_state(Initial, Steps, EndState, Nsteps) :- 
	0 #< Nsteps,
	LeftSteps #= Nsteps - 1,
	make(Initial, Something, NewState),
	Steps = [make(Something)| NewSteps],
	next_state(NewState, NewSteps, EndState, LeftSteps).


bowl_in_inventory(inventory(Lst)) :-
	member(Cell, Lst), 
	member(object('Bowl'), Cell).

plank_in_inventory(inventory(Lst)) :-
	member(Cell, Lst),
	member(object('Plank'), Cell).

wood_in_inventory(inventory(Lst)) :-
	member(Cell, Lst),
	member(object(wood(_)), Cell).

stone_in_inventory(inventory(Lst)) :-
	member(Cell, Lst),
	member(object(stone(_)), Cell).

plan_for_bowl(Steps) :-
	make_inventory(Lst),
        length(Steps, L),	
	next_state(Lst, Steps, EndState, L), 
	bowl_in_inventory(EndState).

