# RBX-Scrapper, By: Euronymou5
# https://github.com/Euronymou5
# Discord: euronymou5

import re
from playwright.sync_api import Playwright, sync_playwright, expect
import time
import requests
from datetime import datetime
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich import print as print_rich
from rich.prompt import Prompt
from fake_useragent import UserAgent

ua = UserAgent(os='Windows')
global usuario
logo = f"""[gold1]
╦═╗╔╗ ═╗ ╦   ╔═╗┌─┐┬─┐┌─┐┌─┐┌─┐┌─┐┬─┐
╠╦╝╠╩╗╔╩╦╝───╚═╗│  ├┬┘├─┤├─┘├─┘├┤ ├┬┘
╩╚═╚═╝╩ ╚═   ╚═╝└─┘┴└─┴ ┴┴  ┴  └─┘┴└─
         [bold][green_yellow]|By: Euronymou5|
"""

def run(playwright: Playwright) -> None:
    with Progress(
        SpinnerColumn(spinner_name="line"),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    ) as progress:
        task = progress.add_task(f"[bold yellow] Buscando informacion...", total=100)

        while not progress.finished:
            time.sleep(0.013)
            progress.update(task, advance=1)

    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(user_agent=ua.random)
    page = context.new_page()
    page.set_extra_http_headers({
        'Accept-Language': 'es'
    })
    page.goto(f"https://www.roblox.com/user.aspx?username={usuario}")
    page.wait_for_selector("#profile-header-container", timeout=10000)
    page.wait_for_selector("#content", timeout=10000)

    profile_header = page.locator('#profile-header-container')
    otro = page.locator("#content")
    imagen = page.locator(".thumbnail-holder > .thumbnail-2d-container > img")
    
    texto = profile_header.all_inner_texts()
    texto2 = otro.all_inner_texts()

    url = page.url
    patron = r'https:\/\/www\.roblox\.com\/es\/users\/(\d+)\/profile'
    coincidencia = re.search(patron, url)

    response = requests.get(f"https://users.roblox.com/v1/users/{coincidencia.group(1)}")
    data = response.json()

    fecha = data["created"]
    description = data["description"]
    fecha_obj = datetime.fromisoformat(fecha)
    fecha_formateada = fecha_obj.strftime("%d/%m/%Y %H:%M:%S")

    if texto:
        lineas = texto[0].split('\n')
        datos_perfil = {}
    
        try:
            datos_perfil["Nombre de visualización"] = lineas[0]
            datos_perfil["Nombre global"] = lineas[1].lstrip('@')
        
            for linea in lineas[2:-1]:
                partes = linea.split()
                if len(partes) >= 2:
                    clave = ' '.join(partes[1:])
                    valor = partes[0]
                    datos_perfil[clave] = valor
                    
            print_rich('\n[dark_slate_gray2]Detalles del perfil:')
            for clave, valor in datos_perfil.items():
                print_rich(f'[gray42][italic]{clave}: {valor}')
        except IndexError:
            print_rich('\n[red][bold][!] ERROR: [italic]El formato del perfil no es el esperado.')

        print_rich(f'[gray42][italic]Creado en:', fecha_formateada)
        print_rich(f'[gray42][italic]Descripcion:', description)
        print_rich(f'[gray42][italic]Imagen: {imagen.get_attribute("src")}')

    # -------------
    insignias_juegos = []
    insignias_roblox = []

    if texto2:
        lineas = texto2[0].split('\n')
        seccion_actual = None
        for linea in lineas:
            linea = linea.strip()
            if linea == "Insignias de Roblox":
                seccion_actual = "roblox"
                continue
            elif linea == "Insignias":
                seccion_actual = "otras"
                continue
            elif linea == "Estadísticas":
                seccion_actual = None
                break
            
            if seccion_actual == "roblox" and linea and linea != "Ver todo":
                insignias_roblox.append(linea)
            elif seccion_actual == "otras" and linea and linea != "Ver todo":
                insignias_juegos.append(linea)

        print_rich('\n[dark_slate_gray2]Insignias de Roblox:')
        if insignias_roblox:
            for i, ins in enumerate(insignias_roblox):
                print_rich(f"[gray42][italic]{ins}{',' if i < len(insignias_roblox)-1 else ''}")
        else:
            print_rich('\n[dark_red][italic]No se encontraron insignias de Roblox.')
    
        print_rich('\n[dark_slate_gray2]Insigneas de juegos:')
        if insignias_juegos:
            for i, ins in enumerate(insignias_juegos):
                print_rich(f"[gray42][italic]{ins}{',' if i < len(insignias_juegos)-1 else ''}")
        else:
            print_rich('\n[dark_red][italic]No se encontraron insigneas de juegos.')
            
    # ---------------------
    context.close()
    browser.close()

# Checker para comprobar si el usuario existe o no por medio del codigo de respuesta.
def check(usuario):
    r = requests.get(f'https://www.roblox.com/user.aspx?username={usuario}')
    if r.status_code == 404:
        print_rich('\n[red][bold][!] ERROR: [italic]Usuario inexistente.')
        exit()
    else:
        with sync_playwright() as playwright:
            run(playwright)

print_rich(logo)
usuario = Prompt.ask("[sea_green1][bold][~] Ingresa un nombre de usuario")
check(usuario)