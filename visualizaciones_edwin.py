import csv
import random
import math

# ============================================
# VISUALIZACIONES Y ANÁLISIS AVANZADO
# ============================================

# Generar datos de demanda simulada para análisis ABC
random.seed(42)

# Precios por diseño
prices = {
    'T-Shirt': 15,
    'Jeans': 45,
    'Dress': 30
}

# Factor de demanda por talla (basado en distribución típica)
size_demand = {
    'S': 0.8,
    'M': 1.2,
    'L': 1.0,
    'XL': 0.7
}

# Factor de demanda por color (popularidad)
color_demand = {
    'Black': 1.3,
    'White': 1.1,
    'Gray': 0.9,
    'Navy': 0.85,
    'Red': 0.95,
    'Blue': 1.0,
    'Dark Blue': 0.8,
    'Green': 0.7
}

# ============================================
# 1. ANÁLISIS ABC DE SKUs
# ============================================

print("="*80)
print("ANÁLISIS ABC DE SKUs - CLASIFICACIÓN POR VALOR")
print("="*80)

# Generar datos de SKUs con demanda estimada
skus_analysis = []
sku_id = 1

designs = ['T-Shirt', 'Jeans', 'Dress']
sizes = ['S', 'M', 'L', 'XL']
colors_per_design = {
    'T-Shirt': ['Black', 'White', 'Gray', 'Navy', 'Red'],
    'Jeans': ['Blue', 'Black', 'Gray', 'Dark Blue'],
    'Dress': ['Black', 'Red', 'Navy', 'White', 'Green', 'Blue']
}

for design in designs:
    base_demand = 100 if design == 'T-Shirt' else 40 if design == 'Jeans' else 60

    for size in sizes:
        for color in colors_per_design[design]:
            # Calcular demanda mensual estimada
            demand = base_demand * size_demand[size] * color_demand.get(color, 1.0)
            demand = int(demand * random.uniform(0.8, 1.2))  # Variación aleatoria

            revenue = demand * prices[design]

            skus_analysis.append({
                'SKU_ID': f'SKU{sku_id:03d}',
                'Design': design,
                'Size': size,
                'Color': color,
                'Demand_Monthly': demand,
                'Price': prices[design],
                'Revenue_Monthly': revenue
            })
            sku_id += 1

# Ordenar por revenue descendente
skus_analysis.sort(key=lambda x: x['Revenue_Monthly'], reverse=True)

# Calcular totales
total_revenue = sum(sku['Revenue_Monthly'] for sku in skus_analysis)
cumulative = 0

# Clasificar en ABC
for i, sku in enumerate(skus_analysis):
    cumulative += sku['Revenue_Monthly']
    percentage = (cumulative / total_revenue) * 100

    if percentage <= 80:
        sku['Category'] = 'A'
    elif percentage <= 95:
        sku['Category'] = 'B'
    else:
        sku['Category'] = 'C'

    sku['Cumulative_%'] = round(percentage, 1)

# Contar SKUs por categoría
category_counts = {'A': 0, 'B': 0, 'C': 0}
category_revenue = {'A': 0, 'B': 0, 'C': 0}

for sku in skus_analysis:
    category_counts[sku['Category']] += 1
    category_revenue[sku['Category']] += sku['Revenue_Monthly']

# Imprimir resumen ABC
print("\n📊 DISTRIBUCIÓN ABC:")
print("-"*40)
for cat in ['A', 'B', 'C']:
    pct_skus = (category_counts[cat] / len(skus_analysis)) * 100
    pct_revenue = (category_revenue[cat] / total_revenue) * 100
    print(f"Categoría {cat}: {category_counts[cat]:2d} SKUs ({pct_skus:5.1f}%) = ${category_revenue[cat]:,} ({pct_revenue:5.1f}% ingresos)")

# Mostrar top 10 SKUs
print("\n🏆 TOP 10 SKUs POR INGRESOS:")
print("-"*80)
print(f"{'Rank':<5} {'SKU':<8} {'Diseño':<10} {'Talla':<6} {'Color':<10} {'Demanda':>8} {'Ingreso':>10} {'Cat':<4}")
print("-"*80)
for i in range(min(10, len(skus_analysis))):
    sku = skus_analysis[i]
    print(f"{i+1:<5} {sku['SKU_ID']:<8} {sku['Design']:<10} {sku['Size']:<6} {sku['Color']:<10} {sku['Demand_Monthly']:>8} ${sku['Revenue_Monthly']:>9,} {sku['Category']:<4}")

# ============================================
# 2. ESTRATEGIA DIFERENCIADA POR ABC
# ============================================

print("\n" + "="*80)
print("ESTRATEGIA DE INVENTARIO DIFERENCIADA POR CATEGORÍA ABC")
print("="*80)

strategies = {
    'A': {'lot_multiplier': 1.2, 'rop_multiplier': 1.3, 'service_level': 0.98},
    'B': {'lot_multiplier': 1.0, 'rop_multiplier': 1.0, 'service_level': 0.95},
    'C': {'lot_multiplier': 0.8, 'rop_multiplier': 0.7, 'service_level': 0.90}
}

print(f"{'Categoría':<12} {'Service Level':<15} {'Lot Size Factor':<18} {'ROP Factor':<12}")
print("-"*60)
for cat, strat in strategies.items():
    print(f"{cat:<12} {strat['service_level']:<15.0%} {strat['lot_multiplier']:<18.1f} {strat['rop_multiplier']:<12.1f}")

# ============================================
# 3. ACTUALIZAR PARÁMETROS CON ABC
# ============================================

# Base parameters por diseño
base_params = {
    'T-Shirt': {'lot': 25, 'rop': 12},
    'Jeans': {'lot': 45, 'rop': 18},
    'Dress': {'lot': 30, 'rop': 10}
}

# Actualizar parámetros según ABC
for sku in skus_analysis:
    base_lot = base_params[sku['Design']]['lot']
    base_rop = base_params[sku['Design']]['rop']

    category = sku['Category']
    sku['Lot_Size_ABC'] = min(50, int(base_lot * strategies[category]['lot_multiplier']))
    sku['Reorder_Point_ABC'] = int(base_rop * strategies[category]['rop_multiplier'])

# Guardar archivo con parámetros ABC
with open('parametros_inventario_ABC.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['SKU_ID', 'Design', 'Size', 'Color', 'Category_ABC',
                    'Demand_Monthly', 'Revenue_Monthly', 'Lot_Size', 'Reorder_Point'])

    for sku in skus_analysis:
        writer.writerow([
            sku['SKU_ID'],
            sku['Design'],
            sku['Size'],
            sku['Color'],
            sku['Category'],
            sku['Demand_Monthly'],
            sku['Revenue_Monthly'],
            sku['Lot_Size_ABC'],
            sku['Reorder_Point_ABC']
        ])

print("\n✅ Archivo 'parametros_inventario_ABC.csv' creado con clasificación ABC")

# ============================================
# 4. MÉTRICAS DE DESEMPEÑO ESPERADAS
# ============================================

print("\n" + "="*80)
print("MÉTRICAS DE DESEMPEÑO PROYECTADAS")
print("="*80)

# Calcular inventario promedio esperado
total_inventory = 0
for sku in skus_analysis:
    avg_inv = (sku['Lot_Size_ABC'] / 2) + sku['Reorder_Point_ABC']
    total_inventory += avg_inv

print(f"\n📦 INVENTARIO PROMEDIO ESPERADO:")
print(f"   Total: {total_inventory:.0f} unidades")
print(f"   Status: {'✅ CUMPLE' if total_inventory <= 1000 else '❌ EXCEDE'} restricción (≤ 1000)")

# Proyección de ingresos
monthly_revenue = sum(sku['Revenue_Monthly'] for sku in skus_analysis)
revenue_120_days = monthly_revenue * 4  # 120 días = 4 meses

print(f"\n💰 PROYECCIÓN DE INGRESOS:")
print(f"   Mensual: ${monthly_revenue:,.0f}")
print(f"   120 días: ${revenue_120_days:,.0f}")

# Fill rate esperado por categoría
print(f"\n📊 FILL RATE OBJETIVO POR CATEGORÍA:")
for cat, strat in strategies.items():
    count = category_counts[cat]
    print(f"   Categoría {cat} ({count} SKUs): {strat['service_level']:.0%}")

# ============================================
# 5. ANÁLISIS DE CAPACIDAD
# ============================================

print("\n" + "="*80)
print("ANÁLISIS DE CAPACIDAD DE PRODUCCIÓN")
print("="*80)

# Tiempo disponible por día (en minutos)
work_hours = 7.5  # 9am-5pm menos pausas y almuerzo
minutes_per_day = work_hours * 60

# Calcular capacidad diaria por tipo de prenda
setup_time = 38.92  # Cambio de troquel promedio
cutting_time = 20

print(f"\n⏱️ CAPACIDAD DIARIA POR DISEÑO (1 máquina):")
print("-"*50)

for design in designs:
    if design == 'T-Shirt':
        sewing_time = 7.16
    elif design == 'Jeans':
        sewing_time = 27.87
    else:
        sewing_time = 11.42

    # Asumiendo 1 cambio de troquel por lote
    time_per_unit = cutting_time/50 + sewing_time + 1.62  # + QA time
    units_per_day = minutes_per_day / time_per_unit

    print(f"{design:<10}: ~{units_per_day:.0f} unidades/día")

# ============================================
# 6. GRÁFICO ASCII DE DISTRIBUCIÓN ABC
# ============================================

print("\n" + "="*80)
print("DISTRIBUCIÓN VISUAL ABC")
print("="*80)

# Crear gráfico de barras ASCII
max_width = 50
print("\nDistribución de SKUs por Categoría:")
print("-"*60)

for cat in ['A', 'B', 'C']:
    count = category_counts[cat]
    pct = (count / len(skus_analysis)) * 100
    bar_width = int((count / len(skus_analysis)) * max_width)
    bar = '█' * bar_width
    print(f"Cat {cat}: {bar} {count} SKUs ({pct:.1f}%)")

print("\nDistribución de Ingresos por Categoría:")
print("-"*60)

for cat in ['A', 'B', 'C']:
    revenue = category_revenue[cat]
    pct = (revenue / total_revenue) * 100
    bar_width = int((revenue / total_revenue) * max_width)
    bar = '█' * bar_width
    print(f"Cat {cat}: {bar} ${revenue:,} ({pct:.1f}%)")

# ============================================
# 7. RECOMENDACIONES FINALES
# ============================================

print("\n" + "="*80)
print("🎯 RECOMENDACIONES ESTRATÉGICAS")
print("="*80)

print("""
1. PRIORIZACIÓN:
   - Enfocar recursos en SKUs categoría A (mayor impacto en ingresos)
   - Mantener mayor stock de seguridad para productos A

2. OPTIMIZACIÓN:
   - Jeans requiere lotes grandes (45-50) por alto tiempo de setup
   - T-Shirts permiten flexibilidad con lotes menores (20-30)

3. MONITOREO:
   - Revisar clasificación ABC mensualmente
   - Ajustar parámetros según estacionalidad

4. MEJORA CONTINUA:
   - Reducir tiempo de cambio de troquel (38.92 min) es crítico
   - Considerar dedicar máquinas por tipo de prenda
""")

print("="*80)
print("✅ Análisis avanzado completado - Edwin")
print("="*80)