import csv
import math
import statistics

# ============================================
# 1. CARGAR DATOS
# ============================================

def load_csv(filename):
    """Carga un archivo CSV y devuelve una lista de diccionarios"""
    data = []
    with open(filename, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)
    return data

# Cargar datos
die_data = []
with open('archivos_csv/Die_Changover_TimeStudy.csv', 'r', encoding='latin-1') as file:
    reader = csv.reader(file)
    next(reader)  # Saltar header
    for i, row in enumerate(reader):
        if i < 74 and len(row) > 1 and row[1]:
            try:
                die_data.append(float(row[1]))
            except:
                pass

# Cargar datos de costura
sewing_data = {'T-Shirt': [], 'Jeans': [], 'Dress': []}
thread_changes = []
with open('archivos_csv/SewingStation_TimeStudy.csv', 'r', encoding='latin-1') as file:
    reader = csv.DictReader(file)
    for row in reader:
        if row['Task'] == 'Sew Garment':
            design = row['Design']
            if design in sewing_data:
                sewing_data[design].append(float(row['Time (Minutes)']))
        elif row['Task'] == 'Change Thread':
            thread_changes.append(float(row['Time (Minutes)']))

# Cargar datos QA
qa_data = []
with open('archivos_csv/QA Inspection Time.csv', 'r', encoding='latin-1') as file:
    reader = csv.DictReader(file)
    for row in reader:
        if row['Time (Minutes)']:
            qa_data.append(float(row['Time (Minutes)']))

# Cargar material handling
material_data = []
with open('archivos_csv/PickUpDropOffTime.csv', 'r', encoding='latin-1') as file:
    reader = csv.DictReader(file)
    for row in reader:
        if row['Time (Minutes)']:
            material_data.append(float(row['Time (Minutes)']))

# ============================================
# 2. CALCULAR ESTADÍSTICAS
# ============================================

def calc_stats(data, name):
    """Calcula estadísticas básicas"""
    if not data:
        return None
    mean = statistics.mean(data)
    stdev = statistics.stdev(data) if len(data) > 1 else 0
    return {
        'Proceso': name,
        'Media': round(mean, 2),
        'Desv_Est': round(stdev, 2),
        'Min': round(min(data), 2),
        'Max': round(max(data), 2),
        'N': len(data)
    }

# Calcular estadísticas para cada proceso
print("\n" + "="*80)
print("TABLA RESUMEN DE ESTADÍSTICAS DE TIEMPOS")
print("="*80)
print(f"{'Proceso':<25} {'Media':>8} {'Desv.Est':>10} {'Min':>8} {'Max':>8} {'N':>6}")
print("-"*80)

# Cambio de troquel
stats = calc_stats(die_data, 'Cambio Troquel')
if stats:
    print(f"{stats['Proceso']:<25} {stats['Media']:>8} {stats['Desv_Est']:>10} {stats['Min']:>8} {stats['Max']:>8} {stats['N']:>6}")

# Costura por diseño
for design in ['T-Shirt', 'Jeans', 'Dress']:
    stats = calc_stats(sewing_data[design], f'Costura {design}')
    if stats:
        print(f"{stats['Proceso']:<25} {stats['Media']:>8} {stats['Desv_Est']:>10} {stats['Min']:>8} {stats['Max']:>8} {stats['N']:>6}")

# Cambio de hilo
stats = calc_stats(thread_changes, 'Cambio Hilo')
if stats:
    print(f"{stats['Proceso']:<25} {stats['Media']:>8} {stats['Desv_Est']:>10} {stats['Min']:>8} {stats['Max']:>8} {stats['N']:>6}")

# QA
stats = calc_stats(qa_data, 'Inspección QA/Prenda')
if stats:
    print(f"{stats['Proceso']:<25} {stats['Media']:>8} {stats['Desv_Est']:>10} {stats['Min']:>8} {stats['Max']:>8} {stats['N']:>6}")

# Material Handling
stats = calc_stats(material_data, 'Material Handling')
if stats:
    print(f"{stats['Proceso']:<25} {stats['Media']:>8} {stats['Desv_Est']:>10} {stats['Min']:>8} {stats['Max']:>8} {stats['N']:>6}")

# ============================================
# 3. EXPRESIONES PARA SIMIO
# ============================================

print("\n" + "="*80)
print("EXPRESIONES DE DISTRIBUCIÓN PARA SIMIO")
print("="*80)
print(f"{'Proceso':<25} {'Expresión Simio':<45} {'Tipo':<15}")
print("-"*80)

# Corte (constante)
print(f"{'Corte':<25} {'20':<45} {'Constante':<15}")

# Cambio de troquel
mean = statistics.mean(die_data)
stdev = statistics.stdev(die_data)
print(f"{'Cambio Troquel':<25} {f'Random.Normal({mean:.2f}, {stdev:.2f})':<45} {'Normal':<15}")

# Costura por diseño
for design in ['T-Shirt', 'Jeans', 'Dress']:
    mean = statistics.mean(sewing_data[design])
    stdev = statistics.stdev(sewing_data[design])
    print(f"{'Costura ' + design:<25} {f'Random.Normal({mean:.2f}, {stdev:.2f})':<45} {'Normal':<15}")

# Cambio hilo
mean = statistics.mean(thread_changes)
stdev = statistics.stdev(thread_changes)
print(f"{'Cambio Hilo':<25} {f'Random.Normal({mean:.2f}, {stdev:.2f})':<45} {'Normal':<15}")

# QA
mean = statistics.mean(qa_data)
stdev = statistics.stdev(qa_data)
print(f"{'QA/Prenda':<25} {f'Random.Normal({mean:.2f}, {stdev:.2f})':<45} {'Normal':<15}")

# Material Handling
mean = statistics.mean(material_data)
stdev = statistics.stdev(material_data)
print(f"{'Material Handling':<25} {f'Random.Normal({mean:.2f}, {stdev:.2f})':<45} {'Normal':<15}")

# ============================================
# 4. GENERAR ESTRUCTURA DE SKUs
# ============================================

print("\n" + "="*80)
print("ESTRUCTURA DE SKUs")
print("="*80)

designs = ['T-Shirt', 'Jeans', 'Dress']
sizes = ['S', 'M', 'L', 'XL']
colors = {
    'T-Shirt': ['Black', 'White', 'Gray', 'Navy', 'Red'],
    'Jeans': ['Blue', 'Black', 'Gray', 'Dark Blue'],
    'Dress': ['Black', 'Red', 'Navy', 'White', 'Green', 'Blue']
}

total_skus = 0
skus_by_design = {}

for design in designs:
    count = len(sizes) * len(colors[design])
    skus_by_design[design] = count
    total_skus += count

print(f"Total de SKUs: {total_skus}")
for design in designs:
    print(f"- {design}: {skus_by_design[design]} SKUs ({len(sizes)} tallas × {len(colors[design])} colores)")

# ============================================
# 5. ESTRATEGIA INICIAL DE INVENTARIO
# ============================================

print("\n" + "="*80)
print("ESTRATEGIA INICIAL DE INVENTARIO POR DISEÑO")
print("="*80)
print(f"{'Diseño':<15} {'Lot Size':<12} {'Reorder Point':<15} {'Tiempo Proc (min)':<20} {'Justificación':<40}")
print("-"*80)

strategies = [
    ('T-Shirt', 25, 12, 7.16, 'Proceso rápido, baja variabilidad'),
    ('Jeans', 45, 18, 27.87, 'Alto tiempo setup, mayor variabilidad'),
    ('Dress', 30, 10, 11.42, 'Tiempo medio, demanda moderada')
]

for design, lot, rop, time, just in strategies:
    print(f"{design:<15} {lot:<12} {rop:<15} {time:<20.2f} {just:<40}")

# ============================================
# 6. CREAR ARCHIVO CSV DE PARÁMETROS
# ============================================

# Crear archivo CSV con parámetros iniciales
with open('parametros_inventario_inicial.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['SKU_ID', 'Design', 'Size', 'Color', 'Lot_Size', 'Reorder_Point'])

    sku_id = 1
    for design in designs:
        # Determinar parámetros según diseño
        if design == 'T-Shirt':
            lot_size, reorder_point = 25, 12
        elif design == 'Jeans':
            lot_size, reorder_point = 45, 18
        else:  # Dress
            lot_size, reorder_point = 30, 10

        for size in sizes:
            for color in colors[design]:
                writer.writerow([
                    f'SKU{sku_id:03d}',
                    design,
                    size,
                    color,
                    lot_size,
                    reorder_point
                ])
                sku_id += 1

print("\n✅ Archivo 'parametros_inventario_inicial.csv' creado con éxito")

# ============================================
# 7. MATRIZ DE EXPERIMENTOS
# ============================================

print("\n" + "="*80)
print("DISEÑO DE EXPERIMENTOS")
print("="*80)

lot_sizes = {
    'T-Shirt': [20, 25, 30],
    'Jeans': [40, 45, 50],
    'Dress': [25, 30, 35]
}

reorder_points = {
    'T-Shirt': [10, 12, 15],
    'Jeans': [15, 18, 20],
    'Dress': [8, 10, 12]
}

# Crear matriz de experimentos
with open('matriz_experimentos.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Exp_ID', 'Design', 'Lot_Size', 'Reorder_Point', 'Status'])

    exp_id = 1
    for design in designs:
        for lot in lot_sizes[design]:
            for rop in reorder_points[design]:
                writer.writerow([
                    f'EXP{exp_id:03d}',
                    design,
                    lot,
                    rop,
                    'Pendiente'
                ])
                exp_id += 1

print(f"Total de experimentos diseñados: {exp_id - 1}")
print("✅ Archivo 'matriz_experimentos.csv' creado con éxito")

# ============================================
# 8. RESUMEN FINAL
# ============================================

print("\n" + "="*80)
print("RESUMEN DE ANÁLISIS COMPLETADO - EDWIN")
print("="*80)
print("\n📊 ARCHIVOS GENERADOS:")
print("1. parametros_inventario_inicial.csv - Parámetros para 52 SKUs")
print("2. matriz_experimentos.csv - 27 combinaciones experimentales")
print("\n📈 MÉTRICAS CLAVE PARA SIMIO:")
print("- Inventario promedio máximo: 1000 unidades")
print("- Fill Rate objetivo: ≥ 95% por SKU")
print("- Período de simulación: 120 días")
print("\n✅ Análisis de Fase 2 completado exitosamente")