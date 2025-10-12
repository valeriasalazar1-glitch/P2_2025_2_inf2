import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.io as sio
import os
from typing import Optional, Tuple, Any

#cte
FS = 1000  


class CSV:
    def __init__(self, path: str):
        self.path = path
        self.df: Optional[pd.DataFrame] = None
        self.nombre = os.path.basename(path)
        self._load_csv()

    def _load_csv(self):
        for sep in [';', ',', '\t']:
            try:
                df = pd.read_csv(self.path, sep=sep)
                if df.shape[1] > 1:
                    self.df = df
                    return
            except Exception:
                continue
        self.df = pd.read_csv(self.path)

    def info(self) -> str:
        buf = []
        self.df.info(buf=buf)
        return "\n".join(buf)

    def dtypes(self) -> pd.Series:
        return self.df.dtypes

    def describe(self) -> pd.DataFrame:
        return self.df.describe()

    def scatter(self, col_x: str, col_y: str, title: str, xlabel: str, ylabel: str, save_name: str):
        if col_x not in self.df.columns or col_y not in self.df.columns:
            raise ValueError('Nombre de columna no encontrado')
        plt.figure()
        self.df.plot.scatter(x=col_x, y=col_y)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(save_name, dpi=200)
        plt.close()

    def histogram(self, col: str, bins: int, title: str, xlabel: str, ylabel: str, save_name: str):
        if col not in self.df.columns:
            raise ValueError('Nombre de columna no encontrado')
        plt.figure()
        self.df[col].hist(bins=bins)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(save_name, dpi=200)
        plt.close()

    def index_segment(self, row_min: int, row_max: int, columns: list):
        n = len(self.df)
        if row_min < 0 or row_max >= n or row_min > row_max:
            raise IndexError('rango de filas invalido')
        if isinstance(columns, list):
            for c in columns:
                if c not in self.df.columns:
                    raise KeyError(f'Columna {c} no existe.')
            return self.df.loc[row_min:row_max, columns]
        else:
            raise ValueError('invalido, columns debe ser lista')


class EEG:
    def __init__(self, mat_path: str):
        self.path = mat_path
        self.mat_dict = None
        self.loaded_key = None
        self.data = None 
        self.nombre = os.path.basename(mat_path)
        self.load_mat()

    def load_mat(self):
        self.mat_dict = sio.loadmat(self.path)

    def list_keys(self):
        keys = [k for k in self.mat_dict.keys() if not k.startswith("__")]
        return keys

    def select_key(self, key: str):
        if key not in self.mat_dict:
            raise KeyError('Lave inválida en el archivo .mat')
        arr = self.mat_dict[key]
        if not isinstance(arr, np.ndarray):
            raise ValueError('el valor de la llave no es un array numpy')
        if arr.ndim == 1:
            arr2 = arr.reshape((1, arr.size))
        elif arr.ndim == 2:
            arr2 = arr
        elif arr.ndim == 3:
            canales, puntos, ensayos = arr.shape
            arr2 = np.reshape(arr, (canales, puntos * ensayos), order='F')
        else:
            raise ValueError('El ndarray debe ser 1D, 2D o 3D.')
        self.loaded_key = key
        self.data = arr2
        return arr2

    def get_info(self) -> Tuple[int, Tuple[int, ...]]: 
        if self.data is None:
            return (0, ())
        return (self.data.ndim, self.data.shape)

    def devolver_canal(self, canal: int, pmin: int, pmax: int) -> np.ndarray:
        if self.data is None:
            raise ValueError('no hay datos cargados')
        if canal < 0 or canal >= self.data.shape[0]:
            raise IndexError('Canl no valido')
        if pmin < 0 or pmax > self.data.shape[1] or pmin >= pmax:
            raise IndexError('rango invalido')
        return self.data[canal, pmin:pmax]

    def devolver_segmento(self, pmin: int, pmax: int) -> np.ndarray:
        if self.data is None:
            raise ValueError('no hay datos cargados')
        if pmin < 0 or pmax > self.data.shape[1] or pmin >= pmax:
            raise IndexError('rango invalido')
        return self.data[:, pmin:pmax]

    def contaminar_canal(self, canal: int, pmin: int, pmax: int, seed: Optional[int] = None) -> np.ndarray:
        original = self.devolver_canal(canal, pmin, pmax).copy()
        rng = np.random.default_rng(seed)
        ruido = rng.random(original.shape) 
        contaminado = original + ruido
        return original, contaminado

    def promedio_desviacion(self, eje: int = 0) -> Tuple[np.ndarray, np.ndarray]:
        if self.data is None:
            raise ValueError('no hay datos cargados')
        mean = np.mean(self.data, axis=eje)
        std = np.std(self.data, axis=eje)
        return mean, std
####graficos
    @staticmethod
    def _samples_to_seconds(samples: np.ndarray) -> np.ndarray:
        return samples / FS

    def plot_original_and_contaminated(self, canal: int, pmin: int, pmax: int, save_name: str, title: str = ""):
        original_seg = self.devolver_canal(canal, pmin, pmax)
        _, contaminated_seg = self.contaminar_canal(canal, pmin, pmax)

        t = self._samples_to_seconds(np.arange(pmin, pmax))  # tiempo en segundos para eje x

        fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
        axes[0].plot(t, original_seg)
        axes[0].set_title(f"{title} - Canal {canal} (original)")
        axes[0].set_ylabel('amplitud (µV)')
        axes[0].legend(['Original'])
        axes[0].grid(True)

        axes[1].plot(t, contaminated_seg)
        axes[1].set_title('"{title} - Canal {canal} (contaminado')
        axes[1].set_xlabel('tiempo (s)')
        axes[1].set_ylabel('Amplitud (µV)')
        axes[1].legend(['Contaminado'])
        axes[1].grid(True)

        plt.tight_layout()
        plt.savefig(save_name, dpi=200)
        plt.close()

    def plot_promedio_std_stem(self, eje: int, save_name: str, title_mean: str = 'Promedio', title_std: str = 'Desviacion estandar'):
        mean, std = self.promedio_desviacion(eje)
        fig, axes = plt.subplots(1, 2, figsize=(12, 4))

        axes[0].stem(mean, use_line_collection=True)
        axes[0].set_title(title_mean)
        axes[0].set_xlabel('Sensores' if mean.ndim == 1 else 'indice')
        axes[0].set_ylabel('Promedio (µV)')
        axes[0].grid(True)

        axes[1].stem(std, use_line_collection=True)
        axes[1].set_title(title_std)
        axes[1].set_xlabel('Sensores' if std.ndim == 1 else 'Índice')
        axes[1].set_ylabel('Desviacion (µV)')
        axes[1].grid(True)

        plt.tight_layout()
        plt.savefig(save_name, dpi=200)
        plt.close()

    def plot_segment(self, pmin: int, pmax: int, save_name: str, title: str = 'segmento'):
        seg = self.devolver_segmento(pmin, pmax)
        t = self._samples_to_seconds(np.arange(pmin, pmax))
        fig, ax = plt.subplots(figsize=(10, 5))
        if seg.ndim == 1:
            ax.plot(t, seg)
            ax.legend(['canal'])
        else:
            for c in range(seg.shape[0]):
                ax.plot(t, seg[c, :] + c * (np.max(np.abs(seg)) * 1.2))
        ax.set_title(title)
        ax.set_xlabel('tiempo(s)')
        ax.set_ylabel('amplitud(µV)')
        ax.grid(True)
        plt.tight_layout()
        plt.savefig(save_name, dpi=200)
        plt.close()


class Repository:
    def __init__(self):
        self.store = {}

    def add(self, key: str, obj: Any):
        self.store[key] = obj

    def get(self, key: str) -> Any:
        return self.store.get(key, None)

    def list_keys(self):
        return list(self.store.keys())

    def find_by_partial(self, substring: str):
        return [k for k in self.store.keys() if substring.lower() in k.lower()]
