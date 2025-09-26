from ursina import *
from PIL import Image
from pathlib import Path, PurePath


class SpritesheetLoader:
    def __init__(self, spritesheet_path):
        """
        Простой загрузчик спрайтшитов

        Args:
            spritesheet_path: Путь к PNG файлу спрайтшита
        """
        self.spritesheet_path = spritesheet_path
        self.spritesheet = Image.open(spritesheet_path)
        self.textures = {}

        # Создаем каталог temp если его нет
        self.temp_dir = Path("temp")
        self.temp_dir.mkdir(exist_ok=True)

    def get_sprite(self, x, y, w, h, name=None):
        """
        Вырезает спрайт из спрайтшита

        Args:
            x, y: Координаты левого верхнего угла
            width, height: Размеры спрайта
            name: Имя для кеширования (опционально)

        Returns:
            Texture: Готовая текстура для Ursina
        """
        # Проверяем кеш в памяти
        cache_key = name or f"{x}_{y}_{w}_{h}"
        if cache_key in self.textures:
            return self.textures[cache_key]

        # Составляем путь к временному файлу
        temp_filename = f"sprite_{cache_key}.png"
        temp_path = PurePath(self.temp_dir, temp_filename)

        # Проверяем, существует ли уже файл
        if Path(temp_path).exists():
            # Загружаем существующий файл
            texture = load_texture(str(temp_path))
        else:
            # Создаем новый спрайт
            sprite = self.spritesheet.crop((x, y, x + w, y + h))
            sprite.save(temp_path)
            texture = load_texture(str(temp_path))

        # Кешируем в памяти
        self.textures[cache_key] = texture

        return texture

    def get_sprites_grid(self, start_x, start_y, sprite_width, sprite_height,
                         cols, rows, names=None):
        """
        Получает сетку спрайтов (удобно для анимации)

        Args:
            start_x, start_y: Начальные координаты сетки
            sprite_width, sprite_height: Размер одного спрайта
            cols, rows: Количество столбцов и строк
            names: Список имен для спрайтов (опционально)

        Returns:
            list: Список текстур
        """
        sprites = []

        for row in range(rows):
            for col in range(cols):
                x = start_x + col * sprite_width
                y = start_y + row * sprite_height

                name = None
                if names:
                    index = row * cols + col
                    if index < len(names):
                        name = names[index]

                sprite = self.get_sprite(x, y, sprite_width, sprite_height, name)
                sprites.append(sprite)

        return sprites

    def clear_cache(self):
        """
        Очищает кеш в памяти и удаляет временные файлы
        """
        self.textures.clear()

        # Удаляем все временные файлы спрайтов
        for temp_file in self.temp_dir.glob("sprite_*.png"):
            temp_file.unlink()