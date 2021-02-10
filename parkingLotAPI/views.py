from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Slot
from .serializers import SlotSerializer
import json, time, math


# Create your views here.

parkingLotSize = 10;
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
myRequests = {}
timeWindowInSec = 10
noOfAllowedRequests = 5

def rateLimiter(request):
    ipAddrOfRequest = getVisitorIpAddress(request)
    currRequestTime = time.time()
    currRequestTime = math.trunc(currRequestTime)     # converting time into seconds

    if ipAddrOfRequest in myRequests.keys():
        while len(myRequests[ipAddrOfRequest])>0 and myRequests[ipAddrOfRequest][0]<=(currRequestTime-timeWindowInSec):
            myRequests[ipAddrOfRequest].pop(0)
        if len(myRequests[ipAddrOfRequest])>=noOfAllowedRequests:
            print('Request rejected')
        else:
            print('Request accepted')
            myRequests[ipAddrOfRequest].append(currRequestTime)
    else:
        print('Request accepted')
        queue = []
        queue.append(currRequestTime)
        myRequests[ipAddrOfRequest] = queue



class SlotViewSet(viewsets.ModelViewSet):
    queryset = Slot.objects.all()
    serializer_class = SlotSerializer

    @action(detail=False, methods=['POST'])
    def parkCar(self, request, pk=None):
        if 'car_no' in request.data:
            enteredCarNo = request.data['car_no']
            noOfSlots = Slot.objects.all().count()
            if noOfSlots==0:
                DBInitializer()

            isCarPresent = Slot.objects.filter(carNo=enteredCarNo).exists()
            if isCarPresent:
                allotedSlot = Slot.objects.get(carNo=enteredCarNo)
                return Response(allotedSlot.slotNo, status=status.HTTP_200_OK)
            else:
                noOfAvailableSlots = Slot.objects.filter(isFree=True).count()
                if noOfAvailableSlots == 0:
                    resp = {'Message': 'No Slots available'}
                    return Response(resp, status=status.HTTP_200_OK)
                else:
                    #print('slots are available')
                    slots = Slot.objects.filter(isFree=True)
                    allotedSlotNo = slots[0].slotNo
                    availableSlot = Slot.objects.get(slotNo=allotedSlotNo)
                    availableSlot.isFree = False
                    availableSlot.carNo = enteredCarNo
                    availableSlot.save()
                    allotedSlot = availableSlot.slotNo
                    return Response(allotedSlot, status=status.HTTP_200_OK)

        else:
            resp = {'Message':'Please provide car no'}
            return Response(resp, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=False, methods=['POST'])
    def unparkCar(self, request, pk=None):
        if 'slot_no' in request.data:
            enteredSlotNo = request.data['slot_no']
            isSlotValid = Slot.objects.filter(slotNo=enteredSlotNo).exists()
            if isSlotValid:
                currSlot = Slot.objects.get(slotNo=enteredSlotNo)
                if currSlot.isFree:
                    resp = {'Message': 'This slot is already free'}
                    return Response(resp, status=status.HTTP_200_OK)
                else:
                    currSlot.isFree = True
                    currSlot.carNo = None
                    currSlot.save()
                    resp = {'Message': 'Success'}
                    return Response(resp, status=status.HTTP_200_OK)
            else:
                resp = {'Message': 'Please enter a valid slot no'}
                return Response(resp, status=status.HTTP_200_OK)

        else:
            resp = {'Message': 'Please provide Slot no'}
            return Response(resp, status=status.HTTP_400_BAD_REQUEST)


    # To get slotNo by carNo
    @action(detail=False, methods=['POST'])
    def getSlotNo(self, request, pk=None):
        if 'car_no' in request.data:
            enteredCarNo = request.data['car_no']
            isCarPresent = Slot.objects.filter(carNo=enteredCarNo).exists()
            if isCarPresent:
                allotedSlot = Slot.objects.get(carNo=enteredCarNo)
                return Response(allotedSlot.slotNo, status=status.HTTP_200_OK)
            else:
                resp = {'Message': 'Car is not present'}
                return Response(resp, status=status.HTTP_200_OK)

        else:
            resp = {'Message': 'Please provide car no'}
            return Response(resp, status=status.HTTP_400_BAD_REQUEST)


    # To get carNo by slotNo
    @action(detail=False, methods=['POST'])
    def getCarNo(self, request, pk=None):
        rateLimiter(request)
        if 'slot_no' in request.data:
            enteredSlotNo = request.data['slot_no']
            isSlotPresent = Slot.objects.filter(slotNo=enteredSlotNo).exists()
            if isSlotPresent:
                currSlot = Slot.objects.get(slotNo=enteredSlotNo)
                if currSlot.isFree:
                    resp = {'Message': 'Car is not present'}
                    return Response(resp, status=status.HTTP_200_OK)
                else:
                    return Response(currSlot.carNo, status=status.HTTP_200_OK)

            else:
                resp = {'Message': 'Please enter a valid slot No'}
                return Response(resp, status=status.HTTP_200_OK)
        else:
            resp = {'Message': 'Please provide slot no'}
            return Response(resp, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def setLotSize(self, request, pk=None):
        if 'size' in request.data:
            global parkingLotSize
            parkingLotSize = int(request.data['size'])
            resp = {'Message': 'Parking Lot size has been set successfuly'}
            return Response(resp, status=status.HTTP_200_OK)
        else:
            resp = {'Message': 'Please provide size'}
            return Response(resp, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def setRateLimiterParams(self, request, pk=None):
        if 'limit' in request.data and 'window' in request.data:
            global timeWindowInSec, noOfAllowedRequests
            timeWindowInSec = int(request.data['window'])
            noOfAllowedRequests = int(request.data['limit'])
            resp = {'Message': 'Rate Limiter parameters have been set successfuly'}
            return Response(resp, status=status.HTTP_200_OK)
        else:
            resp = {'Message': 'Please provide windowTime and limit'}
            return Response(resp, status=status.HTTP_400_BAD_REQUEST)


