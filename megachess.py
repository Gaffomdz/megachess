import asyncio
import json
from random import randint
import sys
import websockets
import numpy as np


async def send(websocket, action, data):
    message = json.dumps(
        {
            'action': action,
            'data': data,
        }
    )
    print(message)
    await websocket.send(message)


async def start(auth_token):
    uri = "ws://megachess.herokuapp.com/service?authtoken={}".format(auth_token)
    while True:
        print('connection to {}'.format(uri))
        async with websockets.connect(uri) as websocket:
            await play(websocket)


async def play(websocket):
    while True:
        try:
            response = await websocket.recv()
            print(f"< {response}")
            data = json.loads(response)
            if data['event'] == 'update_user_list':
                pass
            if data['event'] == 'gameover':
                pass
            if data['event'] == 'ask_challenge':
                # if data['data']['username'] == 'favoriteopponent':
                await send(
                    websocket,
                    'accept_challenge',
                    {
                        'board_id': data['data']['board_id'],
                    },
                )
            if data['event'] == 'your_turn':
                board = list(data['data']['board'])
                tablero = np.array(board)
                n = tablero.reshape(16,16)
                print(n)
                
                def movposible(fr, fc, n):
                    valor = 0
                    piezas = 'pqbkrh'

                    if  n[fr-1][fc] == ' ' or n[fr-1][fc+1] in piezas or n[fr-1][fc-1] in piezas:
                    # el peon puede mover
                        tr = fr-1
                        tc = fc
                        valor = 0.5
                        avanza = [valor, fr, fc, tr, tc]
                        move = avanza

                        if n[fr-1][fc+1] in piezas or n[fr-1][fc-1] in piezas:
                            #el peon puede comer
                            comeizquierda = [0,0,0,0,0]
                            comederecha = [0,0,0,0,0]
                            if n[fr-1][fc+1] in piezas:
                                # el peon puede comer hacia la derecha
                                tr = fr-1
                                tc = fc+1

                                if n[fr-1][fc+1] == 'p':
                                        valor = 1
                                if n[fr-1][fc+1] == 'h':
                                        valor = 2
                                if n[fr-1][fc+1] == 'b':
                                        valor = 3
                                if n[fr-1][fc+1] == 'r':
                                        valor = 4
                                if n[fr-1][fc+1] == 'q':
                                        valor = 5
                                if n[fr-1][fc+1] == 'k':
                                        valor = 6

                                comederecha = [valor, fr, fc, tr, tc]
                                move = comederecha

                            if n[fr-1][fc-1] in piezas:
                                tr = fr-1
                                tc = fc-1
                        # el peon puede comer hacia la izquierda
                                if n[fr-1][fc-1] == 'p':
                                    valor = 1
                                if n[fr-1][fc-1] == 'h':
                                    valor = 2
                                if n[fr-1][fc-1] == 'b':
                                    valor = 3
                                if n[fr-1][fc-1] == 'r':
                                    valor = 4        
                                if n[fr-1][fc-1] == 'q':
                                    valor = 5
                                if n[fr-1][fc-1] == 'k':
                                    valor = 6
                            
                                comeizquierda = [valor,fr,fc,tr,tc]

                            if comeizquierda[0] >= comederecha[0]:
                                move = comeizquierda
                            else:
                                move = comederecha
                        
                        return move   

                for i in range(len(n)):
                    for j in range(len(n)):   
                        p = n[i][j] 
                        if p == 'P':
                            fr = i
                            fc = j
                            if fc != 15:

                                movposible(fr,fc,n)
                                a = movposible(fr,fc,n) 
                                if a != None:
                                    movimiento = [0,0,0,0,0]
                                    if a[0] > movimiento[0]:
                                        movimiento=a
                fr = movimiento[1]
                fc = movimiento[2]
                tr = movimiento[3]
                tc = movimiento[4]                        

                await send(
                    websocket,
                    'move',
                    {
                        'board_id': data['data']['board_id'],
                        'turn_token': data['data']['turn_token'],
                        'from_row': fr,
                        'from_col': fc,
                        'to_row': tr,
                        'to_col': tc,

                    },
                )
                

        except Exception as e:
            print('error {}'.format(str(e)))
            break  # force login again



asyncio.get_event_loop().run_until_complete(start("b3a07e6f-e637-431f-b45a-2d1a5a76e596"))
#if __name__ == '__main__':
 #   if len(sys.argv) >= 2:
  #      auth_token = sys.argv[1]
   #     asyncio.get_event_loop().run_until_complete(start(auth_token))
   # else:
    #    print('please provide your auth_token')