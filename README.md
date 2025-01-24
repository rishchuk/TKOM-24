## Wstępna dokumentacja projektu
## Roman Ishchuk

### Zakładana funkcjonalność i przykłady
#### Język programowania charakteryzuje się następującymi głównymi cechami:
Po pierwsze, ma słabą, dynamiczną typizację, co oznacza, że typy danych nie są ściśle sprawdzane podczas kompilacji, a zmienne mogą zmieniać swój typ podczas wykonywania programu.
Ponadto, domyślna zmienność oznacza, że obiekty mogą być zmieniane po utworzeniu.
Wreszcie, w tym języku przekazywanie argumentów funkcji odbywa się przez wartość, co oznacza, że funkcja otrzymuje tylko kopię obiektu, a nie sam obiekt.


#### Typy danych
W języku występuje tylko kilka rodzajów danych:\
Wartości logiczne. Istnieją dwa rodzaje wartości logicznych: true i false.\
Liczby. W języku występują dwa rodzaje liczb: int i float.\
Ciągi znaków. Ciągi znaków są umieszczone w podwójnych cudzysłowach.


#### Operatory
| Operator                          | Priorytet     | Asocjatywność  |
|-----------------------------------|---------------|----------------|
| ! (operator jednoargumentowy)     | 1 (Najwyższy) | Prawostronny   |
| * i / (mnożenie i dzielenie)      | 2             | Lewostronny    |
| + i - (dodawanie i odejmowanie)   | 3             | Lewostronny    |
| ==, !=, <, <=, >, >= (porównanie) | 4             | Lewostronny    |
| && (logiczne I)                   | 5             | Lewostronny    |
| &#124;&#124; (logiczne LUB)       | 6 (Najniższy) | Lewostronny    |

#### Typy i operatory
Typy int i float obsługują następujące operatory: +, -, *, /, ==, !=, >, >=, <, <=\
Typ string obsługuje następujące operatory: +, *, ==, !=\
Typ bool obsługuje następujące operatory: +, -, *, /, ==, !=, &&, ||

##### Arytmetyka
```
4 * 1 / 2 + 1 - 1      	# 2
4 * 3 / (2 + 1)       	# 4
10.8 / 3.2             	# 3.375
5.5 - 5 * ( -1)         # 10.5
```

##### String + inny typy
```
"1.05" + 1.05           # "1.051.05"
"1.05a" + 1             # "1.05a1"
2 + 1.5 + "gf"          # "3.5gf"
1.5 + 2                 # 3.5
4 + true                # 5
```

##### Porównanie
```
1 == 1                  # true
1 != 2                  # true
1 < 2                   # true
2 > 1                   # true
1 <= 1	                # true
1 >= 2                  # false
(1 == 1) || (1 == 2)    # true
(1 == 1) && (2 == 2)    # true
!(1 == 1)               # false
1 == true               # true
"text" == "text"        # true
"hello" != "world"      # true
```

#### 1. Przykład definicji zmiennych i operacji arytmetycznych:
```
value x                # Deklarowanie zmiennej x
x = 10                 # Ustawinie x na 10
value y = 5            # Deklaracja zmiennej y i przypisanie jej wartości 5
value z = (x + y) * 2  # Deklaracja zmiennej z i obliczenie jej wartości
```

#### 2. Przykład operacji na ciągach znaków:
```
value hello = "Hello, "
value world = "World!"
print hello + world     # Łączenie ciągów znaków i drukowanie wyniku
print(hello * 2)
```

#### 3. Przykład komentarza:
```
# To jest komentarz
```

#### 4. Przykład instrukcji warunkowej if:
```
if z > 10 && hello == "Hello, " {   
    print("z is greater than 10 and hello is Hello, ")
}
```

#### 5. Przykład pętli while:
```
while x > 0 {
    print(x)
    x = x - 1
}
```

#### 6. Przykład definicji i wywołania funkcji:
```
function add(x, y) {
    value z = x + y
    print(z)
}

value a = 10
value b = 5
add(a, b)
```
*Zmienne a i b są zmiennymi typu „Wartość”

#### 7. Przykład rekursywnego wywołania funkcji
```
function add(x) {
    if x == 5 {
        return 
    }
    if x > 5 {
        x = x - 1
        add(x)
    }
}

value a = 8
add(a)
```

#### 8. Przykład na stringu
```
value word = "Hello"
foreach char in word {
    print(char)
}
```

#### 9. Funkcje wbudowane
```
5 + int(2.1)            # 7
```

#### 10. String z atrybutem
```
print(!"shoes".length)  # false
print("shoes".length)   # 5

value a = "hello"
print(a.length)         # 5
```

#### 11. String z metodami
```
print("TeSt".toLower()) # test

value test = "test"
print(test.toUpper())   # TEST
```

#### 12. Logical and
```
true && false  # false
true && true   # true
```
Operator logical and (&&) sprawdza warunki, zwracając wartość fałszywą (false),\
gdy którykolwiek z operandów jest fałszywy, i prawdziwą (true), gdy oba operandy są prawdziwe.\

#### 13. Logical or
```
true || false  # true
true || true   # true
```
Operator logical or (||) sprawdza warunki, zwracając wartość prawdziwą (true),\
gdy którykolwiek z operandów jest prawdziwy, i fałszywą (false), gdy oba operandy są fałszywe.\


#### Słaba, dynamiczna typizacja:
```
value x = 5             # x jest teraz liczbą całkowitą (int)
value x = "hello"       # x jest teraz ciągiem znaków (str)
value x = true          # x jest teraz wartością logiczną (bool)

```

#### Zakresy widoczności zmiennych:
```
value a = 4

function test(t) {
    value a = 3
    print(a)            # 3
    t = t + 1
    print(t)            # 2
}

function main() {
    value t = 1
    test(t)
    print(a)            # 4
    print(t)            # 1
}

main()
```


#### Przekazywanie argumentów funkcji przez wartość:
```
function double_value(x) {
    x = x * 2
    return x
}

value x = 10
print(double_value(x))  # 20
print(x)                # 10
```


### Formalna specyfikacja i składnia języka w notacji EBNF:
```
program = {declaration} ;
declaration = var_declaration | function_definition ;
block =  "{" ,  { statement } , "}" ;

statement = var_declaration
            | if
            | while
            | foreach
            | identifier_or_call, [ "=" , condition ]
            | return ;

var_declaration = "value" , identifier , [ "=" , condition ] ;
       	 
assignment = identifier , "=" , condition ;

if = "if" , condition , block  ;
while = "while" , condition ,  block ;
foreach = "foreach" , identifier , "in" , (identifier | string) , block ;

function_definition = "function" , identifier , "(" , [ identifier , { "," , identifier } ] , ")" , block ;
function_call = identifier , "(" , args , ")" ;
return = "return", [condition] ;

condition = conjuction, { logical_or , conjuction } ;
conjuction = expression, { logical_and , expression} ;
expression  = additive_expression , [ comparison_operator , additive_expression ] ;
additive_expression = term , { add_sub_operator , term } ;
term = factor , { mul_div_operator , factor } ;
factor = ["!" | "-"], (number | string | bool | attr_method | "(" , condition , ")") ;
identifier = letter , { letter | digit | "_"} ;

attr_method = ( identifier_or_call | string ), { ".", identifier_or_call} ;
identifier_or_call = identifier , ["(", args , ")"] ; 
args =  [ condition , { "," , condition } ] ;

number = int_const | float_const ;
float_const = int_const, ".", digit, { digit } ;
int_const  = "0" | digit_non_zero , {digit} ;
bool  = "true" | "false" ;
string = '"' , { character } , '"' ;     (* ESCAPING: \\t = \t *)

comparison_operator = "==" | "!=" | "<" | "<=" | ">" | ">=" ;
logical_and = "&&" ;
logical_or = "||" ;
add_sub_operator = "+" | "-" ;
mul_div_operator = "*" | "/" ;

letter = "A" | "B" | "C" | "D" | "E" | "F" | "G" 
       | "H" | "I" | "J" | "K" | "L" | "M" | "N" 
       | "O" | "P" | "Q" | "R" | "S" | "T" | "U" 
       | "V" | "W" | "X" | "Y" | "Z" | "a" | "b" 
       | "c" | "d" | "e" | "f" | "g" | "h" | "i" 
       | "j" | "k" | "l" | "m" | "n" | "o" | "p" 
       | "q" | "r" | "s" | "t" | "u" | "v" | "w" 
       | "x" | "y" | "z" ;

digit = "0" | digit_non_zero ;
digit_non_zero =  "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" ;
character = letter | digit | special_character ;

special_character = " " | "!" | "#" | "$" | "%" 
                  | "&" | "'" | "(" | ")" | "*" 
                  | "+" | "," | "-" | "." | "/" 
                  | ":" | ";" | "<" | "=" | ">" 
                  | "?" | "@" | "[" | "]" | "^" 
                  | "_" | "`" | "{" | "|" | "}" 
                  | "~" ;
```

### Obsługa błędów
W przypadku napotkania błędu, zgłaszany jest odpowiedni wyjątek, praca nie jest kontynuowana i użytkownik otrzymuje komunikat o błędzie.\
Komunikaty o błędach mogą zawierać informacje o mejsce błędu, gdzie zostsał napotkany.
```
Variable 'x' not defined: Line: 1, Column: 7
```

```
Expected 'in': Line: 21, Column: 14
```

```
Invalid count of args for add: Line: 7, Column: 10
```

```
Expected '}' to close block: Line: 5, Column 1
```

### Sposób uruchomienia

Instalacja
```
git clone https://github.com/rishchuk/TKOM-24.git
cd TKOM-24
```

Może być uruchamiany z wiersza poleceń, gdzie użytkownik podaje plik źródłowy (z rozszerzeniem .xd) jako argument.

Po wykonaniu interpretera, można oczekiwać wyjście na konsoli.
```
python main.py [file.xd]
```

### Analiza wymagań funkcjonalnych i niefunkcjonalnych

#### Wymagania funkcjonalne:

Interpretacja prostego języka programowania z obsługą zmiennych, operacji matematycznych, logicznych, instrukcji warunkowych i pętli.\
Możliwość definiowania i wywoływania funkcji.\
Wsparcie dla operacji na ciągach znaków.

#### Wymagania niefunkcjonalne:

Wysoka wydajność i niezawodność interpretera.\
Obsługa błędów z odpowiednimi komunikatami.

### Opis sposobu realizacji:

Modułów:

Token i Lexer odpowiedzialne za analizę leksykalną.\
Environment, Interpreter do obsługi semantyki języka i wykonywania kodu.\
Parser, który analizuje strukturę kodu i generuje drzewo składniowe.\
Environment zarządza zmiennymi i funkcjami.


Interakcje między modułami:

Lexer przetwarza źródło i generuje sekwencję tokenów.\
Parser analizuje tokeny, tworzy drzewo składniowe i generuje instrukcje, które są wykonywane przez Interpreter.


### Sposób testowania
Testowanie projektu polega na przygotowaniu testów jednostkowych i integracyjnych, które sprawdzają poprawność analizy leksykalnej, składniowej i semantycznej. Przykłady testów obejmują:

Sprawdzanie poprawności analizy leksykalnej, czy tokeny są generowane prawidłowo.\
Analizę składniową, czy parser prawidłowo interpretuje strukturę kodu.\
Wykonywanie testów na różnych przykładach z różnymi operacjami matematycznymi, logicznymi i operacjami na ciągach znaków.
Obsługę błędów, takie jak próby użycia niezadeklarowanych zmiennych lub funkcji.


#### Testy folder

Testy jednostkowe znajdują się w folderze "tests" i są uruchamiane za pomocą unittest.\
Mamy testy działania interpretera, parsera i lexera.\
W interpreterze testują  różne aspekty tym deklaracje zmiennych, definicje i wywołania funkcji, instrukcje warunkowe, pętle, operacje arytmetyczne i logiczne, operacje na stringu\
oraz funkcje wbudowane. Testy obejmują przypadki poprawne, jak i błędne