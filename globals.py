from scene_manager import SceneManager
from ursina import scene, destroy, Entity

DEBUG_MODE = False  # Отключить перед сборкой
PRESSED_KEYS = False

scene_manager = SceneManager()

def change_scene(name: str):
    if scene_manager:
        scene_manager.switch(name)
    else:
        print("SCENE MANAGER NOT AVAILABLE")


def stop_all_animations_and_invokes():
    """
    Останавливает все текущие анимации и события invoke() в проекте Ursina
    """
    try:
        # Очищаем sequences из глобального приложения
        from ursina import application
        if hasattr(application, 'sequences'):
            sequences_to_kill = list(application.sequences)
            for seq in sequences_to_kill:
                if hasattr(seq, 'kill'):
                    seq.kill()

        # Очищаем все invoke и sequence объекты среди entities
        entities_to_destroy = []
        sequences_destroyed = 0

        if hasattr(scene, 'entities'):
            for entity in list(scene.entities):
                should_destroy = False

                # Ищем объекты с именем класса, указывающим на invoke/sequence
                class_name = entity.__class__.__name__
                if class_name in ['Func', 'Wait', 'Sequence']:
                    should_destroy = True
                    sequences_destroyed += 1

                # Ищем объекты с характерными методами для invoke
                if hasattr(entity, 'func') and hasattr(entity, 'delay'):
                    should_destroy = True

                if should_destroy:
                    entities_to_destroy.append(entity)

        for entity in entities_to_destroy:
            if entity in scene.entities:
                if hasattr(entity, 'kill'):
                    entity.kill()
                else:
                    destroy(entity)

        animations_stopped = 0
        if hasattr(scene, 'entities'):
            for entity in list(scene.entities):
                if hasattr(entity, 'stop_animations'):
                    entity.stop_animations()
                    animations_stopped += 1

                # Также останавливаем animate_* методы вручную
                if hasattr(entity, 'animations') and entity.animations:
                    entity.animations.clear()


        print(f"Остановлено: {len(entities_to_destroy)} invoke/sequence, {animations_stopped} анимаций объектов")

    except Exception as e:
        print(f"Ошибка при остановке анимаций: {e}")


def stop_entity_animations(entity):
    """
    Останавливает все анимации конкретного Entity объекта
    """
    try:
        if not isinstance(entity, Entity):
            print("Переданный объект не является Entity")
            return

        if hasattr(entity, 'stop_animations'):
            entity.stop_animations()

        if hasattr(entity, 'animations'):
            entity.animations.clear()

        print(f"Анимации объекта {entity} остановлены")

    except Exception as e:
        print(f"Ошибка при остановке анимаций объекта: {e}")


def clear_all_invokes():
    """
    Очищает только invoke события, оставляя анимации нетронутыми
    """
    try:
        entities_to_destroy = []

        if hasattr(scene, 'entities'):
            for entity in list(scene.entities):
                if (hasattr(entity, 'step') and
                        callable(getattr(entity, 'step', None)) and
                        hasattr(entity, 't')):
                    entities_to_destroy.append(entity)

        for entity in entities_to_destroy:
            if entity in scene.entities:
                destroy(entity)

        print(f"Очищено {len(entities_to_destroy)} invoke событий")

    except Exception as e:
        print(f"Ошибка при очистке invoke: {e}")


def clear_all_sequences():
    """
    Останавливает только Sequence анимации
    """
    try:
        count = 0
        entities_to_destroy = []

        if hasattr(scene, 'entities'):
            for entity in list(scene.entities):
                # Ищем Sequence объекты по признакам
                if (hasattr(entity, 'kill') and hasattr(entity, 'paused')) or \
                        entity.__class__.__name__ in ['Sequence', 'Func', 'Wait']:
                    entities_to_destroy.append(entity)

        for entity in entities_to_destroy:
            if entity in scene.entities:
                if hasattr(entity, 'kill'):
                    entity.kill()
                else:
                    destroy(entity)
                count += 1

        print(f"Остановлено {count} Sequence анимаций")

    except Exception as e:
        print(f"Ошибка при остановке Sequence: {e}")