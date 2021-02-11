from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Slot
from .serializers import SlotSerializer
import json, time, math
from decouple import config

# Create your views here.

# Declaring global variable for size of of parking lot
parkingLotSize = int(config('PARKING_LOT_SIZE'))
def DBInitializer():
    for x in range(parkingLotSize):
        obj1 = Slot.objects.create(slotNo=x+1, isFree=True)


def getVisitorIpAddress(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

# Declaring map of ipAddr as a key and queue of request times as value, globally
requests = {}
timeWindowInSec = int(config('TIME_WINDOW'))
noOfAllowedRequests = int(config('ALLOWED_REQUESTS'))

def rateLimiter(request):
    ipAddrOfRequest = getVisitorIpAddress(request)
    currRequestTime = time.time()
    currRequestTime = math.trunc(currRequestTime)     # converting time into seconds
    if ipAddrOfRequest in requests.keys():
        while len(requests[ipAddrOfRequest])>0 and requests[ipAddrOfRequest][0]<=(currRequestTime - timeWindowInSec):
            requests[ipAddrOfRequest].pop(0)
        if len(requests[ipAddrOfRequest])>=noOfAllowedRequests:
            #print('Request rejected')
            return False
        else:
            #print('Request accepted')
            requests[ipAddrOfRequest].append(currRequestTime)
            return True
    else:
        #print('Request accepted')
        queue = []
        queue.append(currRequestTime)
        requests[ipAddrOfRequest] = queue
        return True

class SlotViewSet(viewsets.ModelViewSet):
    queryset = Slot.objects.all()
    serializer_class = SlotSerializer

    @action(detail=False, methods=['POST'])
    def parkCar(self, request, pk=None):
        print(timeWindowInSec)
        print(noOfAllowedRequests)
        if rateLimiter(request) is False:
            jsonResp = {
                'Message': 'Request rejected.'
            }
            return JsonResponse(jsonResp, safe=False)
        if 'car_no' in request.data:
            enteredCarNo = request.data['car_no']
            noOfSlots = Slot.objects.all().count()
            if noOfSlots==0:
                DBInitializer()
            isCarPresent = Slot.objects.filter(carNo=enteredCarNo).exists()
            if isCarPresent:
                allotedSlot = Slot.objects.get(carNo=enteredCarNo)
                jsonResp = {
                    'Message':'Car is already present in the parking lot.',
                    'Allotted slot no is': allotedSlot.slotNo
                }
                return JsonResponse(jsonResp, safe=False)
            else:
                noOfAvailableSlots = Slot.objects.filter(isFree=True).count()
                if noOfAvailableSlots == 0:
                    jsonResp = {'Message': 'No Slots available'}
                    return JsonResponse(jsonResp, safe=False)
                else:
                    slots = Slot.objects.filter(isFree=True)
                    allotedSlotNo = slots[0].slotNo
                    availableSlot = Slot.objects.get(slotNo=allotedSlotNo)
                    availableSlot.isFree = False
                    availableSlot.carNo = enteredCarNo
                    availableSlot.save()
                    allotedSlot = availableSlot.slotNo
                    jsonResp = {
                        'Message': 'Slot has been successfully allotted to car.',
                        'Allotted slot no is': allotedSlot
                    }
                    return JsonResponse(jsonResp, safe=False)
        else:
            jsonResp = {
                'Message': 'Please provide car no',
            }
            return JsonResponse(jsonResp, safe=False)

    @action(detail=False, methods=['POST'])
    def unparkCar(self, request, pk=None):
        if rateLimiter(request) is False:
            jsonResp = {
                'Message': 'Request rejected.'
            }
            return JsonResponse(jsonResp, safe=False)
        if 'slot_no' in request.data:
            enteredSlotNo = request.data['slot_no']
            isSlotValid = Slot.objects.filter(slotNo=enteredSlotNo).exists()
            if isSlotValid:
                currSlot = Slot.objects.get(slotNo=enteredSlotNo)
                if currSlot.isFree:
                    jsonResp = {
                        'Message': 'This slot is already free',
                    }
                    return JsonResponse(jsonResp, safe=False)
                else:
                    currSlot.isFree = True
                    currSlot.carNo = None
                    currSlot.save()
                    jsonResp = {
                        'Message': 'Car has been successfully unparked'
                    }
                    return JsonResponse(jsonResp, safe=False)
            else:
                jsonResp = {
                    'Message': 'Please enter a valid slot no.'
                }
                return JsonResponse(jsonResp, safe=False)
        else:
            jsonResp = {
                'Message': 'Please provide slot no.'
            }
            return JsonResponse(jsonResp, safe=False)


    # To get slotNo by carNo
    @action(detail=False, methods=['POST'])
    def getSlotNo(self, request, pk=None):
        if rateLimiter(request) is False:
            jsonResp = {
                'Message': 'Request rejected.'
            }
            return JsonResponse(jsonResp, safe=False)
        if 'car_no' in request.data:
            enteredCarNo = request.data['car_no']
            isCarPresent = Slot.objects.filter(carNo=enteredCarNo).exists()
            if isCarPresent:
                allotedSlot = Slot.objects.get(carNo=enteredCarNo)
                jsonResp = {
                    'Given car no is' : enteredCarNo,
                    'Allotted slot no is': allotedSlot.slotNo
                }
                return JsonResponse(jsonResp, safe=False)
            else:
                jsonResp = {
                    'Message': 'Car is not present in the parking lot'
                }
                return JsonResponse(jsonResp, safe=False)
        else:
            jsonResp = {
                'Message': 'Please provide car no.'
            }
            return JsonResponse(jsonResp, safe=False)
            #return Response(resp, status=status.HTTP_400_BAD_REQUEST)


    # To get carNo by slotNo
    @action(detail=False, methods=['POST'])
    def getCarNo(self, request, pk=None):
        if rateLimiter(request) is False:
            jsonResp = {
                'Message': 'Request rejected.'
            }
            return JsonResponse(jsonResp, safe=False)
        if 'slot_no' in request.data:
            enteredSlotNo = request.data['slot_no']
            isSlotPresent = Slot.objects.filter(slotNo=enteredSlotNo).exists()
            if isSlotPresent:
                currSlot = Slot.objects.get(slotNo=enteredSlotNo)
                if currSlot.isFree:
                    jsonResp = {
                        'Message': 'Entered slot is free'
                    }
                    return JsonResponse(jsonResp, safe=False)
                else:
                    jsonResp = {
                        'Given slot no is' : enteredSlotNo,
                        'Car parked at given slot is': currSlot.carNo
                    }
                    return JsonResponse(jsonResp, safe=False)
            else:
                jsonResp = {
                    'Message': 'Please enter a valid slot No'
                }
                return JsonResponse(jsonResp, safe=False)
        else:
            jsonResp = {
                'Message': 'Please provide slot no.'
            }
            return JsonResponse(jsonResp, safe=False)

    @action(detail=False, methods=['POST'])
    def setLotSize(self, request, pk=None):
        if rateLimiter(request) is False:
            jsonResp = {
                'Message': 'Request rejected.'
            }
            return JsonResponse(jsonResp, safe=False)
        if 'size' in request.data:
            global parkingLotSize
            parkingLotSize = int(request.data['size'])
            jsonResp = {
                'Message': 'Parking Lot size has been set successfully'
            }
            return JsonResponse(jsonResp, safe=False)
        else:
            jsonResp = {
                'Message': 'Please provide size'
            }
            return JsonResponse(jsonResp, safe=False)

    @action(detail=False, methods=['POST'])
    def setRateLimiterParams(self, request, pk=None):
        if 'limit' in request.data and 'window' in request.data:
            global timeWindowInSec, noOfAllowedRequests
            timeWindowInSec = int(request.data['window'])
            noOfAllowedRequests = int(request.data['limit'])
            jsonResp = {
                'Message': 'Rate Limiter parameters have been set successfully.'
            }
            return JsonResponse(jsonResp, safe=False)
        else:
            jsonResp = {
                'Message': 'Please provide windowTime and limit.'
            }
            return JsonResponse(jsonResp, safe=False)


