-- Top sucursales por facturación
SELECT sucursal, SUM(importe) AS importe_total, SUM(ordenes) AS ordenes
FROM ventas_diarias
GROUP BY sucursal
ORDER BY importe_total DESC;

-- Evolución diaria total
SELECT fecha, SUM(importe) AS importe
FROM ventas_diarias
GROUP BY fecha
ORDER BY fecha;
