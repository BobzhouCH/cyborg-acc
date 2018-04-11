# Copyright 2018 Lenovo Research Co.,LTD.
# All Rights Reserved.
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""create ports table  migration.

Revision ID: e41080397351
Revises: Coco-Gao 
Create Date: 2018-01-26 17:34:36.010417

"""

# revision identifiers, used by Alembic.
revision = 'e41080397351'
down_revision = 'f50980397351'


from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'ports',
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', sa.String(length=36), nullable=False),
        sa.Column('computer_node', sa.String(length=36), nullable=False),
        sa.Column('phy_port_name', sa.String(length=255), nullable=False),  #physical eth port
        sa.Column('pci_slot', sa.String(length=255), nullable=False),
        sa.Column('product_id', sa.Text(), nullable=False),
        sa.Column('vendor_id', sa.Text(), nullable=False),
        sa.Column('is_used', sa.Integer(), nullable=False),  # 1 represents status:used, 0 represents status not-used.
        sa.Column('accelerator_id', sa.String(length=36), nullable=True),   #accelerator uuid
        sa.Column('bind_instance_id', sa.String(length=36), nullable=True),  #nova instance uuid
        sa.Column('bind_port_id', sa.String(length=36), nullable=True),  #neutron logical port uuid
        sa.Column('device_type', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        mysql_ENGINE='InnoDB',
        mysql_DEFAULT_CHARSET='UTF8'
    )

def downgrade():
    op.drop_table('ports')
