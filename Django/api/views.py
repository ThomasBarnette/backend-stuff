from rest_framework import viewsets
from .models import Class, User
from .serializers import ClassSerializer, UserSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
import re


class ClassViewSet(viewsets.ModelViewSet):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    @action(detail=False, methods=['delete'])
    def delete_everything(self, request, pk=None):
        Class.objects.all().delete();
        return Response({"message": "All users have been deleted."}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'])
    def add_class(self, request, pk=None):
        required_fields = \
            ["class_name", "class_name_long", "room", "description", "crn", "days", "time", "instructor", "section", "type"]
        missing_fields = [field for field in required_fields if field not in request.data]

        if missing_fields:
            return Response(
                {"error": f"Missing required fields: {', '.join(missing_fields)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = {
            "course_id": request.data["class_name"],  # Map class_name to title in the model
            "course_name": request.data["class_name_long"],
            "description": request.data["description"],
            "crn": request.data["crn"],
            "days": request.data["days"],
            "time": request.data["time"],
            "instructor": request.data["instructor"],
            "room": request.data["room"],
            "section": request.data["section"],
            "type": request.data["type"]
        }

        serializer = ClassSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # Handle serialization errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['delete'])
    def delete_class(self, request, pk=None):
        if "crn" not in request.data or "id" not in request.data:
            return Response(
                {"error": f"Missing required fields: crn or row id"},
                status=status.HTTP_400_BAD_REQUEST)
        crn = request.query_params.get('crn')
        id = request.query_params.get('id')
        if crn:
            try:
                class_instance = Class.objects.get(crn=crn)
                class_instance.delete()
                return Response({"message": f"Class with CRN {crn} deleted successfully."}, status=status.HTTP_200_OK)
            except Class.DoesNotExist:
                return Response({"error": f"Class with CRN {crn} not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            try:
                class_instance = Class.objects.get(id=id)
                class_instance.delete()
                return Response({"message": f"Class with id {id} deleted successfully."}, status=status.HTTP_200_OK)
            except Class.DoesNotExist:
                return Response({"error": f"Class with id {id} not found."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    def get_users_in_class(self, request, pk=None):
        if "course_id" not in request.data and "crn" not in request.data:
            return Response({"error": "Missing course id or crn"}, status=status.HTTP_400_BAD_REQUEST)
        if "crn" in request.data:
            try:
                crn = request.data["crn"]
                class_instance_1 = Class.objects.get(crn=crn)
                course_id = class_instance_1.course_id
                type = class_instance_1.type
                users = User.objects.filter(classes__course_id=course_id, classes__type=type).distinct().values(
                    "first_name", "last_name", "roster", "id", "classes__section"
                )

                user_data = [
                    {
                        "first_name": user["first_name"],
                        "last_name": user["last_name"],
                        "roster": user["roster"],
                        "section": user["classes__section"],
                        "id": user["id"],
                    }
                    for user in users
                ]

                return Response(
                    {"course_id": course_id, "users": user_data},
                    status=status.HTTP_200_OK,
                )
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        elif "type" in request.data:
            try:
                course_id = request.data["course_id"]
                type = request.data["type"]
                users = User.objects.filter(classes__course_id=course_id, classes__type=type).distinct().values(
                    "first_name", "last_name", "roster", "classes__section"
                )

                user_data = [
                    {
                        "first_name": user["first_name"],
                        "last_name": user["last_name"],
                        "roster": user["roster"],
                        "section": user["classes__section"],
                    }
                    for user in users
                ]

                return Response(
                    {"course_id": course_id, "users": user_data},
                    status=status.HTTP_200_OK,
                )
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": "Gave course_id without type"}, status=status.HTTP_400_BAD_REQUEST)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    @action(detail=False, methods=['post'])
    def create_user(self, request, pk=None):
        required_fields = \
            ["first_name", "last_name", "roster"]
        missing_fields = [field for field in required_fields if field not in request.data]

        if missing_fields:
            return Response(
                {"error": f"Missing required fields: {', '.join(missing_fields)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = {
            "first_name": re.sub(r"\s+", "", request.data["first_name"]),
            "last_name": re.sub(r"\s+", "", request.data["last_name"]),
            "roster": request.data["roster"],
            "classes": 0
        }
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def add_classes_to_user(self, request, pk=None):
        required_fields = \
            ["crn_list", "id"]
        missing_fields = [field for field in required_fields if field not in request.data]
        if missing_fields:
            return Response(
                {"error": f"Missing required fields: {', '.join(missing_fields)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        id = request.data["id"]

        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            return Response({"error": f"User with id {id} not found."}, status=status.HTTP_404_NOT_FOUND)


        crn_arr = request.data["crn_list"]
        print(crn_arr)
        invalid_classes = []
        for crn in crn_arr:
            try:
                class_instance = Class.objects.get(crn=crn)
                user.classes.add(class_instance)
                user.crns.append(crn)
                user.save()
            except Class.DoesNotExist:
                invalid_classes.append(crn)
        return Response(status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def update_associated_courses(self, request, pk=None):
        required_fields = \
            ["id"]
        missing_fields = [field for field in required_fields if field not in request.data]
        if missing_fields:
            return Response(
                {"error": f"Missing required fields: {', '.join(missing_fields)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        id = request.data["id"]
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            return Response({"error": f"User with id {id} not found."}, status=status.HTTP_404_NOT_FOUND)
        invalid_classes = []
        for crn in user.crns:
            print("user_crns: " + crn)
            try:
                class_instance = Class.objects.get(crn=crn)
                user.classes.add(class_instance)
                print("hello")
            except Class.DoesNotExist:
                invalid_classes.append(crn)
                print("invalid: " + invalid_classes)
        return Response(status=status.HTTP_201_CREATED)
    @action(detail=False, methods=['post'])
    def get_user_id(self, request, pk=None):
        required_fields = \
            ["first_name", "last_name"]
        missing_fields = [field for field in required_fields if field not in request.data]
        if missing_fields:
            return Response(
                {"error": f"Missing required fields: {', '.join(missing_fields)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        first_name = request.data["first_name"]
        last_name = request.data["last_name"]
        try:
            user = User.objects.get(first_name=first_name, last_name=last_name)
        except User.DoesNotExist:
            data = {"user_exists": False}
            return Response(data, status.HTTP_200_OK)
        data = {"id": user.id}
        return Response(data, status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def does_user_exist(self, request, pk=None):
        required_fields = \
            ["first_name", "last_name"]
        missing_fields = [field for field in required_fields if field not in request.data]
        if missing_fields:
            return Response(
                {"error": f"Missing required fields: {', '.join(missing_fields)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        first_name = request.data["first_name"]
        last_name = request.data["last_name"]
        try:
            user = User.objects.get(first_name=first_name, last_name=last_name)
        except User.DoesNotExist:
            data = {"user_exists": False}
            return Response(data, status.HTTP_200_OK)
        data = {"user_exists": True}
        return Response(data, status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def get_user_info(self, request):
        # Check for ID first
        if "id" in request.data:
            try:
                user = User.objects.get(id=request.data["id"])
            except User.DoesNotExist:
                return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Check for required fields
            required_fields = ["first_name", "last_name"]
            missing_fields = [field for field in required_fields if field not in request.data]
            if missing_fields:
                return Response(
                    {"error": f"Missing required fields: {', '.join(missing_fields)}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                #update
                first_name = request.data["first_name"]
                last_name = request.data["last_name"]
                user = User.objects.get(first_name=first_name, last_name=last_name)
            except User.DoesNotExist:
                return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)

        # Fetch and serialize class data
        try:
            classes = user.classes.all()
            class_data = [
                {
                    "crn": cls.crn,
                    "course_id": cls.course_id,
                    "course_name_long": cls.course_name,
                    "description": cls.description,
                    "instructor": cls.instructor,
                    "days": cls.days,
                    "time": cls.time,
                    "room": cls.room,
                    "section": cls.section,
                    "type": cls.type,
                }
                for cls in classes
            ]
            return Response(
                {"first_name": user.first_name, "last_name": user.last_name, "classes": class_data, "crns": user.crns},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['delete'])
    def delete_user_classes(self, request, pk=None):
        required_fields = \
            ["crn_list", "first_name", "last_name"]
        missing_fields = [field for field in required_fields if field not in request.data]
        if missing_fields:
            return Response(
                {"error": f"Missing required fields: {', '.join(missing_fields)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        first_name = request.data["first_name"]
        last_name = request.data["last_name"]

        try:
            user = User.objects.get(first_name=first_name, last_name=last_name)
        except User.DoesNotExist:
            return Response({"error": f"User with name {first_name + ' ' + last_name} not found."},
                            status=status.HTTP_404_NOT_FOUND)

        crn_arr = request.data["crn_list"]
        crns_removed = []
        failed_to_remove = []
        for crn in crn_arr:
            try:
                class_instance = Class.objects.get(crn=crn)
                user.classes.remove(class_instance)
                crns_removed.append(crn)
            except Class.DoesNotExist:
                failed_to_remove.append(crn)
        data = {
            "removed": crns_removed,
            "failed": failed_to_remove
        }
        return Response(data, status=status.HTTP_200_OK)
