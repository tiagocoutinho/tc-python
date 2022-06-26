from dolphin.manager import get_manager

from motion import Motor


cfg = {
    'th': Motor('th', {}),
    'tth': Motor('tth', {}),
    'chi': Motor('chi', {}),
    'phi': Motor('phi', {})
}


manager = get_manager()
