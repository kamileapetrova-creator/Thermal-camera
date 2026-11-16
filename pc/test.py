import serial
import tkinter as tk


# ---------- nustatymai ----------

PORT = "COM4"
ser = serial.Serial(PORT, 921600, timeout=1)

FRAME_LEN = 1 + 5040 * 2 + 2    # flags + kadro duomenys + suma


# ---------- ryšys su FPGA ----------

def send(letter, v):
    """Siunčia 3 baitus: raidę, aukštąjį baitą, žemąjį baitą."""
    v = v & 0xFFFF
    ser.write(bytes([ord(letter), v >> 8, v & 0xFF]))


def read_values():
    """Palaukia kito kadro ir grąžina (X, Y, Z) iš jo galo, arba None."""
    ser.reset_input_buffer()
    window = b""
    while window != b"\xDE\xAD\xBE\xEF":
        b = ser.read(1)
        if not b:
            return None
        window = (window + b)[-4:]
    data = ser.read(FRAME_LEN + 5)
    if len(data) < FRAME_LEN + 5:
        return None
    extra = data[FRAME_LEN:]
    x = int.from_bytes(extra[0:2], "big", signed=True)
    y = int.from_bytes(extra[2:4], "big", signed=True)
    z = extra[4]
    return x, y, z


def clamp(v, lo, hi):
    """Neleidžia išeiti už ribų."""
    return max(lo, min(hi, v))


# ---------- mygtukų veiksmai ----------

def set_box(box, value):
    """Išvalo laukelį ir įrašo naują reikšmę."""
    box.delete(0, tk.END)
    box.insert(0, str(value))


def on_get():
    status.config(text="Laukiu reikšmių iš FPGA...")
    root.update()
    values = read_values()
    if values is None:
        status.config(text="Negavau reikšmių (ar dega LED 0?)")
        return
    x, y, z = values
    set_box(x_box, x)
    set_box(y_box, y)
    set_box(z_box, z)
    status.config(text=f"Gauta: X={x} Y={y} Z={z}")


def on_send():
    try:
        x = clamp(int(x_box.get()), -300, 300)
        y = clamp(int(y_box.get()), -300, 300)
        z = clamp(int(z_box.get()), 32, 255)
    except ValueError:
        status.config(text="Įveskite sveikus skaičius!")
        return
    send("x", x)
    send("y", y)
    send("z", z)
    status.config(text=f"Išsiųsta: X={x} Y={y} Z={z}")


# ---------- langas ----------

root = tk.Tk()
root.title("Terminės kameros valdymas")

tk.Label(root, text="X:").grid(row=0, column=0, padx=5, pady=2)
x_box = tk.Entry(root, width=8)
x_box.grid(row=0, column=1)

tk.Label(root, text="Y:").grid(row=1, column=0, padx=5, pady=2)
y_box = tk.Entry(root, width=8)
y_box.grid(row=1, column=1)

tk.Label(root, text="Z:").grid(row=2, column=0, padx=5, pady=2)
z_box = tk.Entry(root, width=8)
z_box.grid(row=2, column=1)

tk.Button(root, text="Siųsti", width=16, command=on_send).grid(row=3, column=0, columnspan=2, pady=(8, 2))
tk.Button(root, text="Gauti reikšmes", width=16, command=on_get).grid(row=4, column=0, columnspan=2, pady=2)

status = tk.Label(root, text="")
status.grid(row=5, column=0, columnspan=2, pady=5)

root.after(200, on_get)     
root.mainloop()             