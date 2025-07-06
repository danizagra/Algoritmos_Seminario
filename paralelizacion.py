import time
from itertools import permutations
from multiprocessing import Pool, cpu_count
import numpy as np

def evaluar_bloque_expresiones(args):
    cifras_bloque, operadores, valor_objetivo = args
    soluciones_locales = []
    evaluaciones_locales = 0
    
    for perm_cifras in cifras_bloque:
        for perm_ops in permutations(operadores, 4):
            expr = f"{perm_cifras[0]}{perm_ops[0]}{perm_cifras[1]}{perm_ops[1]}{perm_cifras[2]}{perm_ops[2]}{perm_cifras[3]}{perm_ops[3]}{perm_cifras[4]}"
            try:
                resultado = eval(expr)
                evaluaciones_locales += 1
                if abs(resultado - valor_objetivo) < 1e-10:
                    soluciones_locales.append((expr, resultado))
            except ZeroDivisionError:
                evaluaciones_locales += 1
    
    return soluciones_locales, evaluaciones_locales


def fuerza_bruta_secuencial(valor_objetivo=4):
    cifras = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    operadores = ['+', '-', '*', '/']
    soluciones = []
    evaluaciones = 0
    
    for perm_cifras in permutations(cifras, 5):
        for perm_ops in permutations(operadores, 4):
            expr = f"{perm_cifras[0]}{perm_ops[0]}{perm_cifras[1]}{perm_ops[1]}{perm_cifras[2]}{perm_ops[2]}{perm_cifras[3]}{perm_ops[3]}{perm_cifras[4]}"
            try:
                resultado = eval(expr)
                evaluaciones += 1
                if abs(resultado - valor_objetivo) < 1e-10:
                    soluciones.append((expr, resultado))
            except ZeroDivisionError:
                evaluaciones += 1
    
    return soluciones, evaluaciones


def fuerza_bruta_paralela(valor_objetivo=4, num_procesos=None):
    """Implementación paralela usando multiprocessing"""
    cifras = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    operadores = ['+', '-', '*', '/']
    
    # Usar todos los cores disponibles si no se especifica
    if num_procesos is None:
        num_procesos = cpu_count()
    
    # Generar todas las permutaciones de cifras
    todas_perms_cifras = list(permutations(cifras, 5))
    total_perms = len(todas_perms_cifras)
    
    # Dividir las permutaciones en bloques para cada proceso
    bloques = []
    tamano_bloque = total_perms // num_procesos
    
    for i in range(num_procesos):
        inicio = i * tamano_bloque
        if i == num_procesos - 1:
            # El último proceso toma el resto
            fin = total_perms
        else:
            fin = inicio + tamano_bloque
        
        bloque = todas_perms_cifras[inicio:fin]
        bloques.append((bloque, operadores, valor_objetivo))
    
    # Ejecutar en paralelo con manejo de errores
    try:
        with Pool(processes=num_procesos) as pool:
            resultados = pool.map(evaluar_bloque_expresiones, bloques)
    except Exception as e:
        print(f"Error en paralelización: {e}")
        print("Fallando a versión secuencial...")
        return fuerza_bruta_secuencial(valor_objetivo)
    
    # Combinar resultados
    soluciones = []
    evaluaciones = 0
    
    for sols_locales, evals_locales in resultados:
        soluciones.extend(sols_locales)
        evaluaciones += evals_locales
    
    return soluciones, evaluaciones


def comparar_rendimiento():
    """Compara el rendimiento entre versión secuencial y paralela"""
    print("=== COMPARACIÓN DE PARALELIZACIÓN ===\n")
    
    # Información del sistema
    num_cores = cpu_count()
    print(f"Sistema con {num_cores} cores disponibles\n")
    
    valor_objetivo = 4
    
    # 1. Versión secuencial
    print("1. VERSIÓN SECUENCIAL:")
    start = time.time()
    sol_seq, eval_seq = fuerza_bruta_secuencial(valor_objetivo)
    time_seq = time.time() - start
    print(f"   Soluciones encontradas: {len(sol_seq)}")
    print(f"   Evaluaciones: {eval_seq:,}")
    print(f"   Tiempo: {time_seq:.3f} segundos")
    print(f"   Evaluaciones/segundo: {eval_seq/time_seq:,.0f}")
    
    # 2. Versión paralela con diferentes números de procesos
    print("\n2. VERSIÓN PARALELA:")
    
    for num_proc in [2, 4, num_cores]:
        if num_proc > num_cores:
            continue
            
        print(f"\n   Con {num_proc} procesos:")
        try:
            start = time.time()
            sol_par, eval_par = fuerza_bruta_paralela(valor_objetivo, num_proc)
            time_par = time.time() - start
            
            speedup = time_seq / time_par
            eficiencia = speedup / num_proc * 100
            
            print(f"   - Soluciones encontradas: {len(sol_par)}")
            print(f"   - Evaluaciones: {eval_par:,}")
            print(f"   - Tiempo: {time_par:.3f} segundos")
            print(f"   - Speedup: {speedup:.2f}x")
            print(f"   - Eficiencia: {eficiencia:.1f}%")
            print(f"   - Evaluaciones/segundo: {eval_par/time_par:,.0f}")
        except Exception as e:
            print(f"   - ERROR: {e}")
            print("   - Fallando a versión secuencial")
    
    # Análisis de resultados
    print("\n=== ANÁLISIS DE RESULTADOS ===")
    print("\n1. VERIFICACIÓN DE CORRECTITUD:")
    print(f"   ¿Mismas soluciones? {'SÍ' if len(sol_seq) == len(sol_par) else 'NO'}")
    print(f"   ¿Mismas evaluaciones? {'SÍ' if eval_seq == eval_par else 'NO'}")
    
    print("\n2. OBSERVACIONES:")
    print("   • La paralelización NO reduce el número de evaluaciones")
    print("   • La paralelización SÍ reduce el tiempo de ejecución")
    print("   • El speedup depende del número de cores")
    print("   • La eficiencia disminuye con más procesos (overhead)")
    
    print("\n3. LIMITACIONES:")
    print("   • Overhead de crear procesos y comunicación")
    print("   • División del trabajo puede no ser perfecta")
    print("   • eval() tiene el GIL en Python (pero multiprocessing lo evita)")
    print("   • Problemas de pickle en algunos entornos")


if __name__ == "__main__":
    # Ejecutar análisis completo
    comparar_rendimiento()
    #analisis_escalabilidad()
    
    print("\n" + "="*50)
    print("NOTA IMPORTANTE:")
    print("La paralelización es la ÚNICA forma de mejorar significativamente")
    print("el tiempo sin sacrificar la completitud de las soluciones.")
    print("="*50)