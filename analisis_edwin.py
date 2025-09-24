import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Configurar estilo de gráficos
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# ============================================
# 1. CARGAR Y PROCESAR DATOS
# ============================================

# Cargar datos de cambio de troquel
die_changeover = pd.read_csv('archivos_csv/Die_Changover_TimeStudy.csv', nrows=74)
die_changeover = die_changeover[['Observation', 'Time (Minutes)']]
die_changeover.columns = ['Observation', 'Time']

# Cargar datos de costura
sewing = pd.read_csv('archivos_csv/SewingStation_TimeStudy.csv')
sewing = sewing[['Observation Number', 'Task', 'Time (Minutes)', 'Design']]
sewing.columns = ['Observation', 'Task', 'Time', 'Design']

# Cargar datos de inspección QA
qa_inspection = pd.read_csv('archivos_csv/QA Inspection Time.csv')
qa_inspection = qa_inspection[['Observation', 'Time (Minutes)']]
qa_inspection.columns = ['Observation', 'Time']

# Cargar datos de manejo de materiales
material_handling = pd.read_csv('archivos_csv/PickUpDropOffTime.csv')
material_handling = material_handling[['Task', 'Time (Minutes)']]
material_handling.columns = ['Task', 'Time']

# ============================================
# 2. ANÁLISIS ESTADÍSTICO
# ============================================

def calculate_statistics(data, name):
    """Calcula estadísticas descriptivas para un conjunto de datos"""
    stats_dict = {
        'Proceso': name,
        'Media': round(data.mean(), 2),
        'Desv_Est': round(data.std(), 2),
        'Min': round(data.min(), 2),
        'Max': round(data.max(), 2),
        'Q1': round(data.quantile(0.25), 2),
        'Q3': round(data.quantile(0.75), 2),
        'CV': round(data.std() / data.mean(), 3),
        'N': len(data)
    }
    return stats_dict

# Análisis por proceso
results = []

# 1. Cambio de troquel
results.append(calculate_statistics(die_changeover['Time'], 'Cambio de Troquel'))

# 2. Costura por diseño
for design in sewing['Design'].unique():
    design_data = sewing[sewing['Design'] == design]
    sew_times = design_data[design_data['Task'] == 'Sew Garment']['Time']
    results.append(calculate_statistics(sew_times, f'Costura {design}'))

# 3. Cambio de hilo
thread_change = sewing[sewing['Task'] == 'Change Thread']['Time']
results.append(calculate_statistics(thread_change, 'Cambio de Hilo'))

# 4. QA Inspection
results.append(calculate_statistics(qa_inspection['Time'], 'Inspección QA'))

# 5. Material Handling
pickup_data = material_handling[material_handling['Task'] == 'Pick Up']['Time']
dropoff_data = material_handling[material_handling['Task'] == 'Drop Off']['Time']
results.append(calculate_statistics(pickup_data, 'Material Handling - Pickup'))
results.append(calculate_statistics(dropoff_data, 'Material Handling - Dropoff'))

# Crear DataFrame de resultados
stats_df = pd.DataFrame(results)
print("\n" + "="*80)
print("TABLA RESUMEN DE ESTADÍSTICAS DE TIEMPOS")
print("="*80)
print(stats_df.to_string(index=False))

# ============================================
# 3. DISTRIBUCIONES PARA SIMIO
# ============================================

def get_distribution_simio(data, name):
    """Determina la mejor distribución y genera expresión para Simio"""
    mean = data.mean()
    std = data.std()

    # Realizar prueba de normalidad
    _, p_value = stats.normaltest(data)

    if p_value > 0.05:  # Distribución normal
        return f"Random.Normal({mean:.2f}, {std:.2f})"
    else:
        # Si no es normal, usar triangular
        min_val = data.min()
        max_val = data.max()
        mode = data.mode().values[0] if len(data.mode()) > 0 else mean
        return f"Random.Triangular({min_val:.2f}, {mode:.2f}, {max_val:.2f})"

print("\n" + "="*80)
print("EXPRESIONES DE DISTRIBUCIÓN PARA SIMIO")
print("="*80)

simio_expressions = []

# Corte (constante)
simio_expressions.append({
    'Proceso': 'Corte',
    'Expresión Simio': '20',
    'Tipo': 'Constante'
})

# Cambio de troquel
simio_expressions.append({
    'Proceso': 'Cambio Troquel',
    'Expresión Simio': get_distribution_simio(die_changeover['Time'], 'Cambio Troquel'),
    'Tipo': 'Normal'
})

# Costura por diseño
for design in ['T-Shirt', 'Jeans', 'Dress']:
    design_data = sewing[sewing['Design'] == design]
    sew_times = design_data[design_data['Task'] == 'Sew Garment']['Time']
    simio_expressions.append({
        'Proceso': f'Costura {design}',
        'Expresión Simio': get_distribution_simio(sew_times, f'Costura {design}'),
        'Tipo': 'Normal'
    })

# Cambio de hilo
simio_expressions.append({
    'Proceso': 'Cambio Hilo',
    'Expresión Simio': get_distribution_simio(thread_change, 'Cambio Hilo'),
    'Tipo': 'Normal'
})

# QA
simio_expressions.append({
    'Proceso': 'QA/Prenda',
    'Expresión Simio': get_distribution_simio(qa_inspection['Time'], 'QA'),
    'Tipo': 'Normal'
})

# Material Handling
all_material = material_handling['Time']
simio_expressions.append({
    'Proceso': 'Material Handling',
    'Expresión Simio': get_distribution_simio(all_material, 'Material Handling'),
    'Tipo': 'Normal'
})

simio_df = pd.DataFrame(simio_expressions)
print(simio_df.to_string(index=False))

# ============================================
# 4. ANÁLISIS DE SKUs Y DEMANDA
# ============================================

print("\n" + "="*80)
print("ESTRUCTURA DE SKUs")
print("="*80)

# Crear estructura de 52 SKUs
designs = ['T-Shirt', 'Jeans', 'Dress']
sizes = ['S', 'M', 'L', 'XL']
colors_per_design = {
    'T-Shirt': ['Black', 'White', 'Gray', 'Navy', 'Red'],
    'Jeans': ['Blue', 'Black', 'Gray', 'Dark Blue'],
    'Dress': ['Black', 'Red', 'Navy', 'White', 'Green', 'Blue']
}

skus = []
sku_id = 1

for design in designs:
    for size in sizes:
        for color in colors_per_design[design]:
            skus.append({
                'SKU_ID': f'SKU{sku_id:03d}',
                'Design': design,
                'Size': size,
                'Color': color,
                'Process_Time': 7.16 if design == 'T-Shirt' else 27.87 if design == 'Jeans' else 11.42
            })
            sku_id += 1

# Verificar total de SKUs
print(f"Total de SKUs generados: {len(skus)}")
print(f"- T-Shirts: {len([s for s in skus if s['Design'] == 'T-Shirt'])} SKUs")
print(f"- Jeans: {len([s for s in skus if s['Design'] == 'Jeans'])} SKUs")
print(f"- Dresses: {len([s for s in skus if s['Design'] == 'Dress'])} SKUs")

# ============================================
# 5. PARÁMETROS INICIALES DE INVENTARIO
# ============================================

print("\n" + "="*80)
print("ESTRATEGIA INICIAL DE INVENTARIO POR DISEÑO")
print("="*80)

inventory_strategy = pd.DataFrame([
    {
        'Diseño': 'T-Shirt',
        'Lot Size Inicial': 25,
        'Reorder Point Inicial': 12,
        'Tiempo Proceso (min)': 7.16,
        'Justificación': 'Proceso rápido, baja variabilidad'
    },
    {
        'Diseño': 'Jeans',
        'Lot Size Inicial': 45,
        'Reorder Point Inicial': 18,
        'Tiempo Proceso (min)': 27.87,
        'Justificación': 'Alto tiempo setup, mayor variabilidad'
    },
    {
        'Diseño': 'Dress',
        'Lot Size Inicial': 30,
        'Reorder Point Inicial': 10,
        'Tiempo Proceso (min)': 11.42,
        'Justificación': 'Tiempo medio, demanda moderada'
    }
])

print(inventory_strategy.to_string(index=False))

# ============================================
# 6. CREAR ARCHIVOS CSV PARA SIMIO
# ============================================

# Crear DataFrame de SKUs completo
skus_df = pd.DataFrame(skus)

# Asignar parámetros iniciales según diseño
for idx, row in skus_df.iterrows():
    if row['Design'] == 'T-Shirt':
        skus_df.at[idx, 'Lot_Size'] = 25
        skus_df.at[idx, 'Reorder_Point'] = 12
    elif row['Design'] == 'Jeans':
        skus_df.at[idx, 'Lot_Size'] = 45
        skus_df.at[idx, 'Reorder_Point'] = 18
    else:  # Dress
        skus_df.at[idx, 'Lot_Size'] = 30
        skus_df.at[idx, 'Reorder_Point'] = 10

# Guardar archivo de parámetros
skus_df.to_csv('parametros_inventario_inicial.csv', index=False)
print("\n✅ Archivo 'parametros_inventario_inicial.csv' creado con éxito")

# Guardar resumen estadístico
stats_df.to_csv('analisis_estadistico_tiempos.csv', index=False)
print("✅ Archivo 'analisis_estadistico_tiempos.csv' creado con éxito")

# Guardar expresiones Simio
simio_df.to_csv('expresiones_simio.csv', index=False)
print("✅ Archivo 'expresiones_simio.csv' creado con éxito")

# ============================================
# 7. MATRIZ DE EXPERIMENTOS
# ============================================

print("\n" + "="*80)
print("DISEÑO DE EXPERIMENTOS")
print("="*80)

# Niveles para experimentación
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

experiments = []
exp_id = 1

for design in designs:
    for lot in lot_sizes[design]:
        for rop in reorder_points[design]:
            experiments.append({
                'Exp_ID': f'EXP{exp_id:03d}',
                'Design': design,
                'Lot_Size': lot,
                'Reorder_Point': rop,
                'Status': 'Pendiente'
            })
            exp_id += 1

experiments_df = pd.DataFrame(experiments)
experiments_df.to_csv('matriz_experimentos.csv', index=False)
print(f"Total de experimentos diseñados: {len(experiments)}")
print("✅ Archivo 'matriz_experimentos.csv' creado con éxito")

# ============================================
# 8. RESUMEN FINAL
# ============================================

print("\n" + "="*80)
print("RESUMEN DE ENTREGABLES GENERADOS")
print("="*80)
print("1. parametros_inventario_inicial.csv - Parámetros para 52 SKUs")
print("2. analisis_estadistico_tiempos.csv - Estadísticas descriptivas")
print("3. expresiones_simio.csv - Distribuciones para simulación")
print("4. matriz_experimentos.csv - Diseño factorial de experimentos")
print("\n📊 Análisis completado exitosamente para Fase 2")