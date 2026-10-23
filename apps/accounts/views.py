from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .forms import StaffLoginForm, StaffCreationForm, StaffEditForm
from .decorators import principal_required
from apps.core.models import AuditLog

User = get_user_model()


def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    if request.method == 'POST':
        form = StaffLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.full_name} ({user.get_role_display()})!")
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('core:dashboard')
        else:
            messages.error(request, "Invalid username/staff ID or password. Please try again.")
    else:
        form = StaffLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "You have been logged out successfully.")
    return redirect('accounts:login')


@login_required
@principal_required
def staff_list_view(request):
    role_filter = request.GET.get('role', '')
    query = request.GET.get('q', '').strip()

    staff_members = User.objects.all().order_by('role', 'first_name', 'last_name')

    if role_filter:
        staff_members = staff_members.filter(role=role_filter)

    if query:
        staff_members = staff_members.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(username__icontains=query) |
            Q(staff_id__icontains=query) |
            Q(email__icontains=query)
        )

    roles = User.Role.choices

    return render(request, 'accounts/staff_list.html', {
        'staff_members': staff_members,
        'roles': roles,
        'selected_role': role_filter,
        'query': query,
    })


@login_required
@principal_required
def staff_create_view(request):
    if request.method == 'POST':
        form = StaffCreationForm(request.POST, request.FILES)
        if form.is_valid():
            staff = form.save()
            AuditLog.objects.create(
                user=request.user,
                action='CREATE_STAFF',
                details=f"Created staff account {staff.full_name} with role {staff.get_role_display()}"
            )
            messages.success(request, f"Staff member {staff.full_name} created successfully.")
            return redirect('accounts:staff_list')
        else:
            messages.error(request, "Please correct the errors in the form below.")
    else:
        form = StaffCreationForm()

    return render(request, 'accounts/staff_form.html', {
        'form': form,
        'title': 'Add New Staff Member',
        'button_text': 'Create Staff Account',
    })


@login_required
@principal_required
def staff_edit_view(request, pk):
    staff = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        form = StaffEditForm(request.POST, request.FILES, instance=staff)
        if form.is_valid():
            form.save()
            AuditLog.objects.create(
                user=request.user,
                action='UPDATE_STAFF',
                details=f"Updated profile for staff {staff.full_name} (Role: {staff.get_role_display()})"
            )
            messages.success(request, f"Staff record for {staff.full_name} updated successfully.")
            return redirect('accounts:staff_list')
        else:
            messages.error(request, "Please check the form for errors.")
    else:
        form = StaffEditForm(instance=staff)

    return render(request, 'accounts/staff_form.html', {
        'form': form,
        'staff': staff,
        'title': f'Edit Staff: {staff.full_name}',
        'button_text': 'Save Changes',
    })


@login_required
def staff_detail_view(request, pk):
    staff = get_object_or_404(User, pk=pk)
    allocations = staff.allocations.select_related('subject', 'class_section', 'academic_session').all()
    managed_classes = staff.managed_classes.all()

    return render(request, 'accounts/staff_detail.html', {
        'staff': staff,
        'allocations': allocations,
        'managed_classes': managed_classes,
    })


@login_required
def profile_view(request):
    return staff_detail_view(request, request.user.pk)
