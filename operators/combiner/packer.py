# Copyright (c) 2011, 2012, 2013, 2014, 2015, 2016 Jake Gordon and contributors
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from typing import Union
from typing import Dict


class BinPacker(object):
    def __init__(self, images: Dict) -> None:
        self.root = {}
        self.bin = images

    def fit(self) -> Dict:
        self.root = {'x': 0, 'y': 0, 'w': 0, 'h': 0}

        if not self.bin:
            return self.bin

        self.root['w'], self.root['h'] = next(iter(self.bin.values()))['gfx']['size']

        for img in self.bin.values():
            w, h = img['gfx']['size']
            node = self.find_node(self.root, w, h)
            img['gfx']['fit'] = self.split_node(node, w, h) if node else self.grow_node(w, h)

        return self.bin

    def find_node(self, root: Dict, w: int, h: int) -> Union[Dict, None]:
        if 'used' in root and root['used']:
            return self.find_node(root['right'], w, h) or self.find_node(root['down'], w, h)
        elif w <= root['w'] and h <= root['h']:
            return root
        return None

    @staticmethod
    def split_node(node: Dict, w: int, h: int) -> Dict:
        node['used'] = True
        node['down'] = {'x': node['x'], 'y': node['y'] + h, 'w': node['w'], 'h': node['h'] - h}
        node['right'] = {'x': node['x'] + w, 'y': node['y'], 'w': node['w'] - w, 'h': h}
        return node

    def grow_node(self, w: int, h: int) -> Union[Dict, None]:     
        can_grow_right = h <= self.root['h']
        can_grow_down = w <= self.root['w']

        should_grow_right = can_grow_right and self.root['h'] >= self.root['w'] + w
        should_grow_down = can_grow_down and self.root['w'] >= self.root['h'] + h

        if should_grow_right or not should_grow_down and can_grow_right:
            return self.grow_right(w, h)
        elif should_grow_down or can_grow_down:
            return self.grow_down(w, h)
        return None

    def grow_right(self, w: int, h: int) -> Union[Dict, None]:
        self.root = {
            'used': True,
            'x': 0,
            'y': 0,
            'w': self.root['w'] + w,
            'h': self.root['h'],
            'down': self.root,
            'right': {'x': self.root['w'], 'y': 0, 'w': w, 'h': self.root['h']}
        }
        node = self.find_node(self.root, w, h)
        return self.split_node(node, w, h) if node else None

    def grow_down(self, w: int, h: int) -> Union[Dict, None]:
        self.root = {
            'used': True,
            'x': 0,
            'y': 0,
            'w': self.root['w'],
            'h': self.root['h'] + h,
            'down': {'x': 0, 'y': self.root['h'], 'w': self.root['w'], 'h': h},
            'right': self.root
        }
        node = self.find_node(self.root, w, h)
        return self.split_node(node, w, h) if node else None
    
### Sable Tweaks
class AlignmentNode():
    def __init__(self, x: int, y: int, vA: int) -> None:
        self.x = x
        self.y = y
        # Vertical Allowance
        self.vA = vA


class SableBinPacker(object):
    images = {}
    atlasWidth = 0
    atlasHeight = 0
    nodesDictionary = {}
    nodesArray = []
    growDirection = 1

    validAtlasSizes = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192]

    def __init__(self, images: Dict) -> None:
        self.images = images

        self.nodesDictionary = {} # <int (y), AlignmentNode>
        self.nodesArray = []

        self.atlasWidth = 0
        self.atlasHeight = 0

        # if > 0, then grow atlas horizontally, if < 0, then grow vertically
        self.growDirection = 1

    def fit(self) -> Dict:

        if not self.images:
            return self.images        

        '''tempDictionary = {}
        iterationCount = 0
        for key, img in self.images.items():
            iterationCount += 1 

            tempDictionary[key] = img

            if iterationCount >= 30:
                break            

        self.images = tempDictionary'''

        print("~~~~~~~~~~~~~~~ [Atlaser]: " + "Fitting!")  

        #iterationCount = 0
        for img in self.images.values():
            w, h = img['gfx']['size']
            x = 0
            y = 0
            
            #iterationCount += 1         

            print("~~~~~~~~~~~~~~~ [Atlaser]: " + "Fitting Next Image: w" + str(w) + " h" + str(h))
            img['gfx']['fit'] = {'x': x, 'y': y, 'w': w, 'h': h}

            # Check to see if this is the first image
            if self.atlasWidth == 0:           
                for i in range(0, len(self.validAtlasSizes)):
                    pwr2 = self.validAtlasSizes[i]
                    if max(w, h) == pwr2:                      
                        self.atlasWidth = pwr2
                        self.atlasHeight = pwr2                  
                        break

                    if max(w, h) < pwr2:                    
                        self.atlasWidth = pwr2
                        self.atlasHeight = pwr2
                        break

                print("~~~~~~~~~~~~~~~ [Atlaser]: " + "Setting Atlas size [w" + str(self.atlasWidth) + " h" + str(self.atlasHeight) + "]")                            
                        
                if self.atlasWidth == 0:
                    print("Error: Cannot be using zero width images")
                    break            

                self.nodesArray.append(AlignmentNode(w, 0, h))
                self.nodesArray.append(AlignmentNode(0, h, 0))

                self.nodesDictionary[0] = self.nodesArray[0]
                self.nodesDictionary[self.atlasHeight] = self.nodesArray[1]               

                print("~~~~~~~~~~~~~~~ [Atlaser]: " + "Putting " + str(w) + "x" + str(h) + " at: [x" + str(x) + " y" + str(y) + "]")

                img['gfx']['fit'] = {'x': x, 'y': y, 'w': w, 'h': h}
                continue

            # determine what node to add this image to
            rightmostNode = self.nodesArray[0]
            lowestNode = self.nodesArray[-1]
            validmostNode = None
            for node in self.nodesArray:
                if node.x > rightmostNode.x:
                    rightmostNode = node

                if node.y > lowestNode.y:
                    lowestNode = node
                
                # vertical allowance check
                if h > node.vA:
                    continue

                if self.atlasWidth - node.x >= w:
                    if self.atlasHeight - node.y >= h:
                        if validmostNode == None:
                            validmostNode = node
                            continue

                        if node.x > validmostNode.x:
                            validmostNode = node

            # evaluate node
            if validmostNode == None:
                # time to expand atalas
                
                if self.growDirection > 0:
                    self.atlasWidth *= 2
                    validmostNode = rightmostNode                    
                else:
                    previousHeight = self.atlasHeight
                    self.atlasHeight *= 2
                    lowestNode.vA = self.atlasHeight-lowestNode.y
                    validmostNode = lowestNode

                self.growDirection *= -1

                #print("~~~~~~~~~~~~~~~ [Atlaser]: " + "GOT HERE 2")

            print("~~~~~~~~~~~~~~~ [Atlaser]: " + "Putting " + str(w) + "x" + str(h) + " Image at: [x" + str(validmostNode.x) + " y" + str(validmostNode.y) + "]")
            img['gfx']['fit'] = {'x': validmostNode.x , 'y': validmostNode.y , 'w': w, 'h': h}

            # Update used Node
            print("~~~~~~~~~~~~~~~ [Atlaser]: " + "Promoting Selected Node: [x" + str(validmostNode.x) + " y" + str(validmostNode.y) + " vA" + str(validmostNode.vA) + "] to [x" + str(validmostNode.x + w) + " y" + str(validmostNode.y) + " vA" + str(h) + "]")
            previousVA = validmostNode.vA
            validmostNode.vA = h
            validmostNode.x += w            

            # Create new node at bottom left of placed image if there isn't a node on the same y value as another
            newNodeY = validmostNode.y + h
            if newNodeY not in self.nodesDictionary:
                print("~~~~~~~~~~~~~~~ [Atlaser]: " + "Adding New Node: [x" + str(validmostNode.x - w) + " y" + str(newNodeY) + " vA" + str(validmostNode.vA-h) + "]")
                newNode = AlignmentNode(validmostNode.x - w, newNodeY, previousVA-h)
                self.nodesArray.append(newNode)
                self.nodesDictionary[newNodeY] = newNode

            # if this current node updates and is sharing the same x position of another remove itself and add its vertical allowance to it
            for otherNode in self.nodesArray:
                if otherNode.x == validmostNode.x and otherNode != validmostNode:
                    #for nI in range(0, len(self.nodesArray)):
                    #    if self.nodesArray[nI] == validmostNode:
                    #        self.nodesArray.pop(nI)
                    #        break
                    print("~~~~~~~~~~~~~~~ [Atlaser]: " + "Removing Node: [x" + str(validmostNode.x) + " y" + str(validmostNode.y) + " vA" + str(validmostNode.vA) + "]")
                    self.nodesArray.remove(validmostNode)
                    del self.nodesDictionary[validmostNode.y]
                    otherNode.vA += validmostNode.vA
                    break





        #w, h = img['gfx']['size']
        #node = self.find_node(self.root, w, h)
        #img['gfx']['fit'] = self.split_node(node, w, h) if node else self.grow_node(w, h)

        return self.images

    '''def find_node(self, root: Dict, w: int, h: int) -> Union[Dict, None]:
        if 'used' in root and root['used']:
            return self.find_node(root['right'], w, h) or self.find_node(root['down'], w, h)
        elif w <= root['w'] and h <= root['h']:
            return root
        return None

    @staticmethod
    def split_node(node: Dict, w: int, h: int) -> Dict:
        node['used'] = True
        node['down'] = {'x': node['x'], 'y': node['y'] + h, 'w': node['w'], 'h': node['h'] - h}
        node['right'] = {'x': node['x'] + w, 'y': node['y'], 'w': node['w'] - w, 'h': h}
        return node

    def grow_node(self, w: int, h: int) -> Union[Dict, None]:     
        can_grow_right = h <= self.root['h']
        can_grow_down = w <= self.root['w']

        should_grow_right = can_grow_right and self.root['h'] >= self.root['w'] + w
        should_grow_down = can_grow_down and self.root['w'] >= self.root['h'] + h

        if should_grow_right or not should_grow_down and can_grow_right:
            return self.grow_right(w, h)
        elif should_grow_down or can_grow_down:
            return self.grow_down(w, h)
        return None

    def grow_right(self, w: int, h: int) -> Union[Dict, None]:
        self.root = {
            'used': True,
            'x': 0,
            'y': 0,
            'w': self.root['w'] + w,
            'h': self.root['h'],
            'down': self.root,
            'right': {'x': self.root['w'], 'y': 0, 'w': w, 'h': self.root['h']}
        }
        node = self.find_node(self.root, w, h)
        return self.split_node(node, w, h) if node else None

    def grow_down(self, w: int, h: int) -> Union[Dict, None]:
        self.root = {
            'used': True,
            'x': 0,
            'y': 0,
            'w': self.root['w'],
            'h': self.root['h'] + h,
            'down': {'x': 0, 'y': self.root['h'], 'w': self.root['w'], 'h': h},
            'right': self.root
        }
        node = self.find_node(self.root, w, h)
        return self.split_node(node, w, h) if node else None'''
###
