# language-cheatsheet
Learn multiple languages at the same time.

| Features/Languages| Python | Go | Rust | Swift | Kotlin| Java | Dart |
|:-----------------:|:--|:--:|:----:|:-----:|:-----:|:--:|:-----:|
| package management tools | pip,conda | go get, go mod | Cargo | Cocoapods, Swift Package Manager | Gradle, Maven | Gradle, Maven | pub |
| frameworks | Django, Flask, FastAPI| Gin, Echo, Beego |  | SwiftUI, Vapor | Ktor, Jetpack, Srping Boot | Spring Boot | Flutter |
memory management | GC | GC | Ownership | ARC | GC | GC | GC |
constant declaration| `myConst = 10` | `const MY_CONST int = 10` | `const MY_CONST:i32 = 10;`  | `let myConst = 10` | `val MyConst = 10` | `final int MY_CONST = 10;` | `const myConst = 10;` or `final myConst; myConst = 10;`|
| comment | `# comment-line` or `'''comment block'''` or `"""comment block"""` |  |  |
|multiple statements in 1 line| |||||
|import modules| `import somemodule` or `from somemodule import function1, function2` | `` | `` | `` | `` | `` |
|variable declaration | `myVar = 10` | `var myVar int; myVar = 10` or `var myVar = 10` or `myVar := 10` | `let mut myVar = 10` | `var myVar:Int` or ` var myVar = 10` | `var myVar:Int` or `var myVar = 10` | `int myVar = 10;` | `var myVar = 10;` |
|Optionals|  |  |  | `var myVar:Int?` | `var myVar:Int?` |  |  |
| print statement| `print("Hello, ", myVar)` | `import "fmt" fmt.Println("Hello",myVar)` |  | `print("Hello, \(myVar) ")` | `println("Hello, $myVar")` | `System.out.println("Hello"+myVar);` | |
| primitive types |  | `` | `` |  | `` | `byte short int long float double boolean char String` | `` |
| types | `int float complex bool String` | `byte rune int uint uintptr float32 float64 complex64 complex128 bool ` |  | `Int UInt Float Double Bool String Character` | `Byte Short Int Long Float Double Boolean String Char` | `byte short int long float double boolean char String` | `` |
|type inference|  | √ |  | √| √ | - |  |
| collection types | `List Tuple Set Dictionary`  |||||
| List | `myList = [ 'abcd', 786 , 2.23 ]` | |||||
| Tuple | `myTuple = ( 'abcd', 786 , 2.23 )` | | ||||
| Dictionary/Map | `myDict = { 'abc': 123, 98.6: 37 }` ||||||
|if statement| `if condition_1:`<br>&nbsp;&nbsp;&nbsp;&nbsp;`statement_block_1`<br>`elif condition_2:`<br>&nbsp;&nbsp;&nbsp;&nbsp;`statement_block_2`<br>`else:`<br>&nbsp;&nbsp;&nbsp;&nbsp;`statement_block_3` ||||||
| function declaration | `def sum(a, b):`<br>&nbsp;&nbsp;&nbsp;&nbsp;`return a + b` | `func sum(a, b int) int { return a + b }` | `fn sum(a: i32, b: i32) -> i32 { return a + b; }` | `func sum(a: Int, b: Int) -> Int { return a + b }` | `fun sum(a: Int, b: Int): Int { return a + b }` | `public class MyClass {`<br>`public static int sum(int a, int b) {`<br>` return a + b;`<br>`}` | |
