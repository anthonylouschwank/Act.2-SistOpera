"""
Scanner Léxico - Procesador de Tokens
Desarrollo manual sin expresiones regulares ni máquinas de estados
"""

class ElementoLexico:
    """Elemento léxico identificado durante el escaneo"""
    def __init__(self, categoria, valor, fila, columna_pos):
        self.categoria = categoria
        self.valor = valor
        self.fila = fila
        self.columna_pos = columna_pos
    
    def mostrar(self):
        return f"ElementoLexico({self.categoria:15s}, '{self.valor:20s}', Fila: {self.fila:3d}, Col: {self.columna_pos:3d})"
    
    def __repr__(self):
        return self.mostrar()


class RegistroIdentificadores:
    """Registro para almacenar y rastrear identificadores encontrados"""
    def __init__(self):
        self.registro = {}
        self.indice = 0
    
    def agregar(self, nombre_id, fila, col):
        """Agrega un identificador al registro o actualiza sus apariciones"""
        if nombre_id not in self.registro:
            self.indice += 1
            self.registro[nombre_id] = {
                'numero': self.indice,
                'identificador': nombre_id,
                'categoria': 'IDENTIFICADOR',
                'primera_vez': (fila, col),
                'usos': [(fila, col)]
            }
        else:
            self.registro[nombre_id]['usos'].append((fila, col))
    
    def buscar(self, nombre_id):
        """Recupera la información de un identificador específico"""
        return self.registro.get(nombre_id, None)
    
    def mostrar_registro(self):
        salida = "\n" + "="*80 + "\n"
        salida += "REGISTRO DE IDENTIFICADORES\n"
        salida += "="*80 + "\n"
        salida += f"{'NUM':5s} | {'IDENTIFICADOR':20s} | {'CATEGORÍA':15s} | {'FILA':6s} | {'COLUMNA':7s} | {'USOS':12s}\n"
        salida += "-"*80 + "\n"
        
        for nombre, datos in sorted(self.registro.items()):
            primera_pos = datos['primera_vez']
            total_usos = len(datos['usos'])
            salida += f"{datos['numero']:5d} | {nombre:20s} | {datos['categoria']:15s} | {primera_pos[0]:6d} | {primera_pos[1]:7d} | {total_usos:12d}\n"
        
        salida += "="*80 + "\n"
        salida += f"Identificadores únicos totales: {len(self.registro)}\n"
        salida += "="*80 + "\n"
        return salida


class ScannerLexico:
    """Scanner que procesa y clasifica elementos léxicos del código"""
    
    # Términos reservados del lenguaje
    TERMINOS_RESERVADOS = {
        'if', 'else', 'while', 'for', 'do', 'break', 'continue',
        'return', 'int', 'float', 'double', 'char', 'void', 'bool',
        'true', 'false', 'null', 'class', 'public', 'private',
        'protected', 'static', 'const', 'new', 'delete', 'this',
        'switch', 'case', 'default', 'struct', 'typedef', 'enum',
        'sizeof', 'import', 'package', 'try', 'catch', 'throw',
        'finally', 'def', 'lambda', 'print', 'input', 'range',
        'var', 'let', 'function', 'string'
    }
    
    # Símbolos de operación
    SIMBOLOS_OPERACION = {
        '+', '-', '*', '/', '%', '=', '==', '!=', '<', '>', '<=', '>=',
        '&&', '||', '!', '&', '|', '^', '~', '<<', '>>', '++', '--',
        '+=', '-=', '*=', '/=', '%=', '&=', '|=', '^=', '->'
    }
    
    # Símbolos delimitadores
    SIMBOLOS_DELIMITADORES = {
        '(', ')', '{', '}', '[', ']', ';', ',', '.', ':'
    }
    
    def __init__(self, texto_fuente):
        self.texto_fuente = texto_fuente
        self.indice_actual = 0
        self.fila_actual = 1
        self.col_actual = 1
        self.elementos_lexicos = []
        self.registro_ids = RegistroIdentificadores()
    
    def simbolo_en_posicion(self):
        """Obtiene el símbolo en la posición de lectura actual"""
        if self.indice_actual < len(self.texto_fuente):
            return self.texto_fuente[self.indice_actual]
        return None
    
    def mover_cursor(self):
        """Mueve el cursor de lectura una posición adelante"""
        if self.indice_actual < len(self.texto_fuente):
            if self.texto_fuente[self.indice_actual] == '\n':
                self.fila_actual += 1
                self.col_actual = 1
            else:
                self.col_actual += 1
            self.indice_actual += 1
    
    def mirar_siguiente(self, desplazamiento=1):
        """Observa símbolos adelante sin mover el cursor"""
        posicion = self.indice_actual + desplazamiento
        if posicion < len(self.texto_fuente):
            return self.texto_fuente[posicion]
        return None
    
    def verificar_alfabetico(self, simbolo):
        """Comprueba si el símbolo es alfabético o guión bajo"""
        if simbolo is None:
            return False
        return (simbolo >= 'a' and simbolo <= 'z') or (simbolo >= 'A' and simbolo <= 'Z') or simbolo == '_'
    
    def verificar_numerico(self, simbolo):
        """Comprueba si el símbolo es un dígito numérico"""
        if simbolo is None:
            return False
        return simbolo >= '0' and simbolo <= '9'
    
    def verificar_blanco(self, simbolo):
        """Comprueba si el símbolo es espacio en blanco"""
        if simbolo is None:
            return False
        return simbolo == ' ' or simbolo == '\t' or simbolo == '\n' or simbolo == '\r'
    
    def ignorar_blancos(self):
        """Omite todos los espacios en blanco consecutivos"""
        while self.simbolo_en_posicion() and self.verificar_blanco(self.simbolo_en_posicion()):
            self.mover_cursor()
    
    def omitir_comentario_simple(self):
        """Omite comentarios de línea única (//)"""
        self.mover_cursor()  # Omite primer /
        self.mover_cursor()  # Omite segundo /
        while self.simbolo_en_posicion() and self.simbolo_en_posicion() != '\n':
            self.mover_cursor()
    
    def omitir_comentario_multiple(self):
        """Omite comentarios de múltiples líneas (/* */)"""
        self.mover_cursor()  # Omite /
        self.mover_cursor()  # Omite *
        while self.simbolo_en_posicion():
            if self.simbolo_en_posicion() == '*' and self.mirar_siguiente(1) == '/':
                self.mover_cursor()  # Omite *
                self.mover_cursor()  # Omite /
                break
            self.mover_cursor()
    
    def capturar_nombre(self):
        """Captura un nombre de identificador o término reservado"""
        fila_inicio = self.fila_actual
        col_inicio = self.col_actual
        secuencia = ""
        
        while self.simbolo_en_posicion() and (self.verificar_alfabetico(self.simbolo_en_posicion()) or 
                                               self.verificar_numerico(self.simbolo_en_posicion())):
            secuencia += self.simbolo_en_posicion()
            self.mover_cursor()
        
        # Determinar si es término reservado o identificador
        if secuencia in self.TERMINOS_RESERVADOS:
            clasificacion = "TERMINO_RESERVADO"
        else:
            clasificacion = "IDENTIFICADOR"
            self.registro_ids.agregar(secuencia, fila_inicio, col_inicio)
        
        return ElementoLexico(clasificacion, secuencia, fila_inicio, col_inicio)
    
    def capturar_valor_numerico(self):
        """Captura un valor numérico (entero o con decimales)"""
        fila_inicio = self.fila_actual
        col_inicio = self.col_actual
        secuencia = ""
        tiene_decimales = False
        
        while self.simbolo_en_posicion() and self.verificar_numerico(self.simbolo_en_posicion()):
            secuencia += self.simbolo_en_posicion()
            self.mover_cursor()
        
        # Revisar presencia de punto decimal
        if self.simbolo_en_posicion() == '.' and self.verificar_numerico(self.mirar_siguiente(1)):
            tiene_decimales = True
            secuencia += self.simbolo_en_posicion()
            self.mover_cursor()
            
            while self.simbolo_en_posicion() and self.verificar_numerico(self.simbolo_en_posicion()):
                secuencia += self.simbolo_en_posicion()
                self.mover_cursor()
        
        clasificacion = "VALOR_DECIMAL" if tiene_decimales else "VALOR_ENTERO"
        return ElementoLexico(clasificacion, secuencia, fila_inicio, col_inicio)
    
    def capturar_texto_literal(self, marcador):
        """Captura una cadena de texto literal"""
        fila_inicio = self.fila_actual
        col_inicio = self.col_actual
        secuencia = marcador
        self.mover_cursor()  # Omite marcador inicial
        
        while self.simbolo_en_posicion() and self.simbolo_en_posicion() != marcador:
            if self.simbolo_en_posicion() == '\\':
                secuencia += self.simbolo_en_posicion()
                self.mover_cursor()
                if self.simbolo_en_posicion():
                    secuencia += self.simbolo_en_posicion()
                    self.mover_cursor()
            else:
                secuencia += self.simbolo_en_posicion()
                self.mover_cursor()
        
        if self.simbolo_en_posicion() == marcador:
            secuencia += self.simbolo_en_posicion()
            self.mover_cursor()
        
        return ElementoLexico("LITERAL_TEXTO", secuencia, fila_inicio, col_inicio)
    
    def capturar_operacion(self):
        """Captura un símbolo de operación"""
        fila_inicio = self.fila_actual
        col_inicio = self.col_actual
        secuencia = ""
        
        # Verificar operadores de dos caracteres primero
        if self.simbolo_en_posicion() and self.mirar_siguiente(1):
            combinacion = self.simbolo_en_posicion() + self.mirar_siguiente(1)
            if combinacion in self.SIMBOLOS_OPERACION:
                secuencia = combinacion
                self.mover_cursor()
                self.mover_cursor()
                return ElementoLexico("SIMBOLO_OPERACION", secuencia, fila_inicio, col_inicio)
        
        # Operador de carácter único
        if self.simbolo_en_posicion():
            secuencia = self.simbolo_en_posicion()
            self.mover_cursor()
        
        return ElementoLexico("SIMBOLO_OPERACION", secuencia, fila_inicio, col_inicio)
    
    def capturar_separador(self):
        """Captura un símbolo delimitador"""
        fila_inicio = self.fila_actual
        col_inicio = self.col_actual
        secuencia = self.simbolo_en_posicion()
        self.mover_cursor()
        
        return ElementoLexico("SIMBOLO_SEPARADOR", secuencia, fila_inicio, col_inicio)
    
    def procesar_codigo(self):
        """Analiza el código completo y extrae todos los elementos léxicos"""
        while self.indice_actual < len(self.texto_fuente):
            self.ignorar_blancos()
            
            if not self.simbolo_en_posicion():
                break
            
            simbolo = self.simbolo_en_posicion()
            
            # Detectar comentarios
            if simbolo == '/' and self.mirar_siguiente(1) == '/':
                self.omitir_comentario_simple()
                continue
            
            if simbolo == '/' and self.mirar_siguiente(1) == '*':
                self.omitir_comentario_multiple()
                continue
            
            # Procesar identificadores y términos reservados
            if self.verificar_alfabetico(simbolo):
                elemento = self.capturar_nombre()
                self.elementos_lexicos.append(elemento)
            
            # Procesar números
            elif self.verificar_numerico(simbolo):
                elemento = self.capturar_valor_numerico()
                self.elementos_lexicos.append(elemento)
            
            # Procesar cadenas literales
            elif simbolo == '"' or simbolo == "'":
                elemento = self.capturar_texto_literal(simbolo)
                self.elementos_lexicos.append(elemento)
            
            # Procesar delimitadores
            elif simbolo in self.SIMBOLOS_DELIMITADORES:
                elemento = self.capturar_separador()
                self.elementos_lexicos.append(elemento)
            
            # Procesar operadores
            elif simbolo in {'+', '-', '*', '/', '%', '=', '!', '<', '>', '&', '|', '^', '~'}:
                elemento = self.capturar_operacion()
                self.elementos_lexicos.append(elemento)
            
            # Símbolo no reconocido
            else:
                fila_inicio = self.fila_actual
                col_inicio = self.col_actual
                elemento = ElementoLexico("NO_RECONOCIDO", simbolo, fila_inicio, col_inicio)
                self.elementos_lexicos.append(elemento)
                self.mover_cursor()
        
        return self.elementos_lexicos
    
    def mostrar_elementos(self):
        """Muestra la lista completa de elementos léxicos encontrados"""
        print("\n" + "="*80)
        print("ELEMENTOS LÉXICOS IDENTIFICADOS")
        print("="*80)
        for numero, elemento in enumerate(self.elementos_lexicos, 1):
            print(f"{numero:4d}. {elemento.mostrar()}")
        print("="*80)
        print(f"Total de elementos: {len(self.elementos_lexicos)}")
        print("="*80)
    
    def generar_resumen(self):
        """Crea un resumen estadístico del análisis"""
        resumen = {}
        for elemento in self.elementos_lexicos:
            resumen[elemento.categoria] = resumen.get(elemento.categoria, 0) + 1
        
        print("\n" + "="*80)
        print("RESUMEN DEL ANÁLISIS")
        print("="*80)
        for categoria, cantidad in sorted(resumen.items()):
            print(f"{categoria:20s}: {cantidad:5d}")
        print("="*80)


def ejecutar_prueba():
    """Punto de entrada para demostración del scanner"""
    
    # Ejemplo de código para analizar
    programa_ejemplo = """
    // Programa de ejemplo
        public class PotionBrewer {
        // Ingredient costs in gold coins
        private static final double HERB_PRICE = 5.50;
        private static final int MUSHROOM_PRICE = 3;
        private String brewerName;
        private double goldCoins;
        private int potionsBrewed;

        public PotionBrewer(String name, double startingGold) {
            this.brewerName = name;
            this.goldCoins = startingGold;
            this.potionsBrewed = 0;
        }

        public static void main(String[] args) {
        PotionBrewer wizard = new PotionBrewer("Gandalf, the Wise", 100.0);
        String[] ingredients = {"Mandrake Root", "Dragon Scale", "Phoenix Feather"};

            wizard.brewHealthPotion(3, 2); // 3 herbs, 2 mushrooms
            wizard.brewHealthPotion(5, 4);

            wizard.printStatus();
        }

        /* Brews a potion if we have enough gold */
        public void brewHealthPotion(int herbCount, int mushroomCount) {
        double totalCost = (herbCount * HERB_PRICE) + (mushroomCount * MUSHROOM_PRICE
        );
        if (totalCost <= this.goldCoins) {
            this.goldCoins -= totalCost; // Deduct the cost
            this.potionsBrewed++;
            System.out.println("Success! Potion brewed for " + totalCost + " gold.");
        } else {
            System.out.println("Not enough gold! Need: " + totalCost);
        }
        }
        // Prints the current brewer status
        public void printStatus() {
        System.out.println("\n=== Brewer Status ===");
        System.out.println("Name: " + this.brewerName);
        System.out.println("Gold remaining: " + this.goldCoins);
        System.out.println("Potions brewed: " + this.potionsBrewed);
        }
    """
    
    print("\nCÓDIGO FUENTE A PROCESAR:")
    print("="*80)
    print(programa_ejemplo)
    print("="*80)
    
    # Inicializar scanner y procesar código
    scanner = ScannerLexico(programa_ejemplo)
    elementos = scanner.procesar_codigo()
    
    # Mostrar resultados del análisis
    scanner.mostrar_elementos()
    print(scanner.registro_ids.mostrar_registro())
    scanner.generar_resumen()


if __name__ == "__main__":
    ejecutar_prueba()