import os
from clases import CSV, EEG, Repository
def prompt_save_name(default_prefix= 'plot'):
    name = input("Nombre del archivo a guardar [default '{}']: ".format(default_prefix)).strip()
    if name == '':
        name = default_prefix
    return name + '.png'

def main_menu():
    repo = Repository()
    while True:
        print('\n Menu principal')
        print('1 | Cargar archivo csv')
        print('2 | Cargar archivo .mat')
        print('3 | Listar archivos cargados')
        print('4 | Buscar archivo por nombre')
        print('5 | Selleccionar archivo por llave')
        print('6 | Salir')
        opcion = input('Ingrese una opcion: ').strip()
        if opcion== '1':
            path = input("Ruta al archivo CSV: ").strip()
            try:
                csvh = CSV(path)
                key = f'CSV::{os.path.basename(path)}'
                repo.add(key, csvh)
                print(f'CSV cargado y almacenado con clave: {key}')
            except Exception as e:
                print("Error cargando CSV:", e)

        elif opcion == '2':
            path = input("Ruta al archivo .mat: ").strip()
            try:
                eegh = EEG(path)
                key = f'MAT::{os.path.basename(path)}'
                repo.add(key, eegh)
                print(f'.mat cargado. Clave: {key}')
            except Exception as e:
                print('Error cargando .mat:', e)

        elif opcion == '3':
            keys = repo.list_keys()
            if not keys:
                print('No hay archivos cargados')
            else:
                for k in keys:
                    print("", k)

        elif opcion == '4':
            q = input('Texto a buscar en nombres: ').strip()
            matches = repo.find_by_partial(q)
            if matches:
                for m in matches:
                    print(" -", m)
            else:
                print('No encontrado')

        elif opcion == '5':
            key = input('ingrese la llave del archivo: ').strip()
            obj = repo.get(key)
            if obj is None:
                print('Llave no encontrada.')
                continue
            if isinstance(obj, CSV):
                csv_menu(obj)
            elif isinstance(obj, EEG):
                eeg_menu(obj)
            else:
                print("Tipo de objeto no soportado.")

        elif opcion == '6':
            print('Finalizando el programa.')
            break
        else:
            print('Opcion invalida. Intente de nuevo.')


def csv_menu(csvh: CSV):
    while True:
        print(f'\n Menu csv: {csvh.nombre}')
        print('1 | Mostrar info() y tipos por columna')
        print('2 | Mostrar describe()')
        print('3 | Scatter plot entre dos columnas')
        print('4 | Histograma de columna')
        print('5 | Indexado (filas/columnas)')
        print('6 | volver')
        opcion = input('Ingrese opcion: ').strip()
        try:
            if  opcion == '1':
                print('info()')
                print(csvh.info())
                print('\n dtypes')
                print(csvh.dtypes())
            elif opcion == '2':
                print('describe()')
                print(csvh.describe())
            elif opcion == '3':
                print('Columnas disponibles:', list(csvh.df.columns))
                colx = input('Columna X: ').strip()
                coly = input('Columna Y: ').strip()
                title = input('Titulo: ').strip()
                xlabel = input('nombre eje X: ').strip()
                ylabel = input('nombre eje Y: ').strip()
                save = prompt_save_name(default_prefix=f'{csvh.nombre}_scatter_{colx}_{coly}')
                csvh.scatter(colx, coly, title or f'{colx} vs {coly}', xlabel or colx, ylabel or coly, save)
                print(f'Scatter guardado como {save}')
            elif opcion == '4':
                print('Columnas disponibles: ', list(csvh.df.columns))
                col = input('Colunmna para histograma: ').strip()
                bins = int(input('Numero de bins: ').strip())
                title = input('Titulo: ').strip()
                xlabel = input('Nombre eje X: ').strip()
                ylabel = input('Nombre eje Y: ').strip()
                save = prompt_save_name(default_prefix=f'{csvh.nombre}_hist_{col}')
                csvh.histogram(col, bins, title or f'Histograma {col}', xlabel or col, ylabel or 'Frecuencia', save_name=save)
                print(f'Histograma guardado como {save}')
            elif opcion == '5':
                print(f'Filas totales: {len(csvh.df)}')
                rmin = int(input('Fila inicial:').strip())
                rmax = int(input('Fila final:').strip())
                print('Columnas disponibles:', list(csvh.df.columns))
                cols = input('Lista de columnas separadas por coma: ').strip().split(',')
                cols = [c.strip() for c in cols if c.strip() != ""]
                seg = csvh.index_segment(rmin, rmax, cols)
                print(seg)
            elif opcion == '6':
                break
            else:
                print('opcion no valida')
        except Exception as e:
            print('Error', e)
            

def eeg_menu(eegh: EEG):
    while True:
        print(f'\n Menu EEG: {eegh.nombre}')
        print('1 | Listar llaves disponibles en .mat')
        print('2 | Seleccionar llave)')
        print('3 | Contaminar canal y graficar')
        print('4 | Promedio y desviacion estandar con stem plot')
        print('5 | Graficar segmento seleccionado')
        print('6 | Ver info de la matriz cargada')
        print('7 | Volver')
    
        opcion = input('Ingrese una opcion: ').strip()
        try:
            if opcion == '1':
                keys = eegh.list_keys()
                print('Llaves encontradas:')
                for i, k in enumerate(keys):
                    print(f'{i}: {k}')
            elif opcion == '2':
                keys = eegh.list_keys()
                print('Llaves encontradas:')
                for i, k in enumerate(keys):
                    print(f'{i}: {k}')
                idx = int(input('Ingrese el numero de la llave:').strip())
                key = keys[idx]
                arr = eegh.select_key(key)
                print(f'Matriz cargada. shape = {arr.shape}')
            elif opcion == '3':
                if eegh.data is None:
                    print('Seleccione una llave')
                    continue
                canal = int(input('Ingrese canal: ').strip())
                pmin = int(input('Punto inicial: ').strip())
                pmax = int(input('Punto final: ').strip())
                save = prompt_save_name(default_prefix=f'{eegh.nombre}_canal{canal}_{pmin}_{pmax}')
                title = input('Titulo:').strip()
                eegh.plot_original_and_contaminated(canal, pmin, pmax, save_name=save, title=title or "")
                print(f'Plot guardado: {save}')
            elif opcion == '4':
                if eegh.data is None:
                    print('Seleccione una llave')
                    continue
                eje = int(input('Eje para calcular promedio: ').strip())
                save = prompt_save_name(default_prefix=f'{eegh.nombre}_mean_std_eje{eje}')
                eegh.plot_promedio_std_stem(eje, save_name=save)
                print(f'Plot guardado: {save}')
            elif opcion == '5':
                if eegh.data is None:
                    print('Seleccione una llave')
                    continue
                pmin = int(input("Punto inicial: ").strip())
                pmax = int(input("Punto final: ").strip())
                save = prompt_save_name(default_prefix=f'{eegh.nombre}_segment_{pmin}_{pmax}')
                title = input("Titulo para la figura: ").strip()
                eegh.plot_segment(pmin, pmax, save_name=save, title=title or "Segmento")
                print(f'Plot guardado: {save}')
            elif opcion=='6':
                info = eegh.get_info()
                print('Info (dim, shape):', info)
            elif opcion=='7':
                break
            else:
                print('opcion no valida')
        except Exception as a:
            print('Error:', a)
           

if __name__ == '__main__':
    main_menu()
